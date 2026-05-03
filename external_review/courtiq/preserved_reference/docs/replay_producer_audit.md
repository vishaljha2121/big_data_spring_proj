# Replay Producer Audit Report

## 1. Overview

The replay producer is responsible for reading curated replay manifest data and publishing point-level tennis events to Kafka. Its role is not limited to simple record forwarding. It acts as a control point that validates source data, applies deterministic transformations, enforces the outbound event contract, and ensures that malformed data is isolated instead of being mixed into the primary event stream.

This audit focuses on the producer's data handling responsibilities, schema enforcement strategy, transformation behavior, Kafka topic usage, and testing outcomes. The overall objective is to confirm that the producer can serve as a reliable bridge between curated replay data and downstream streaming consumers.

---

## 2. Architecture

At a high level, the replay producer follows a staged pipeline:

1. It reads replay records from the curated manifest dataset.
2. It validates each input row against the replay manifest schema.
3. It transforms each valid manifest row into a point-event payload.
4. It validates the transformed event against the point event schema.
5. It publishes valid events to the primary Kafka topic.
6. It routes invalid records or invalid transformed events to a dead letter queue (DLQ).
7. It emits audit and monitoring information for traceability.

This architecture separates input validation, transformation, and output validation into distinct responsibilities. That separation reduces the chance of silently passing invalid data downstream and makes failures easier to diagnose.

---

## 3. Input Data

The replay producer reads from the following curated source:

- Source: `data/replay/manifests/replay_manifest_v1.parquet`
- Schema: `contracts/replay_manifest_schema.json`

The replay manifest is the authoritative structured input for the producer. Each row contains the information needed to reconstruct or replay a tennis point event in a controlled order. The manifest includes:

- replay ordering
- synthetic identifiers
- player and match metadata

`replay_order` is used to preserve deterministic sequencing during replay. Synthetic identifiers provide stable internal linkage for generated events. Player and match metadata provide the context needed for downstream consumers to understand who is playing, which match the point belongs to, and how the event should be interpreted.

Because the producer depends on the manifest as its source of truth, the quality of this dataset directly affects downstream stream quality. That is why input schema validation is treated as a mandatory gate rather than a best-effort check.

---

## 4. Output Data

The replay producer publishes to the following primary destination:

- Topic: `tennis.point.events`
- Schema: `contracts/point_event_schema.json`

Each manifest row is transformed into a Kafka event that represents a single point-level tennis event. The resulting event includes:

- match metadata
- player information
- scoring context
- event timestamp
- schema version

The output event is designed to be consumed by downstream analytics, validation, and streaming applications. That means the event format must remain stable, explicit, and schema-compliant. The inclusion of a schema version is especially important because it allows downstream systems to reason about contract compatibility over time.

---

## 5. Schema Validation Strategy

The producer applies schema validation in two places: before transformation and after transformation. This two-layer approach protects both the ingestion boundary and the publication boundary.

### Input Validation

Each manifest row is validated against:

- `contracts/replay_manifest_schema.json`

Purpose:

- ensure upstream data integrity
- prevent malformed input

Input validation confirms that the producer is operating on data that matches the expected replay manifest contract. This prevents corrupted, incomplete, or structurally invalid rows from entering the transformation stage. Catching problems at this point reduces ambiguity later in the pipeline because failures can be attributed directly to the source record rather than to derived event logic.

### Output Validation

Each Kafka event is validated against:

- `contracts/point_event_schema.json`

Key rules:

- all required fields must be present
- no extra fields allowed (`additionalProperties = false`)
- correct data types enforced

Output validation ensures that the transformation step produces events that strictly conform to the downstream contract. Required-field enforcement guarantees that consumers always receive the minimum viable payload. `additionalProperties = false` prevents accidental leakage of internal or manifest-only fields. Type enforcement prevents schema drift caused by malformed values, inconsistent serialization, or transformation errors.

Together, input and output validation create a defensive pipeline. Invalid source rows are blocked before transformation, and invalid transformed payloads are blocked before publication to the primary topic.

---

## 6. Transformation Logic

The replay producer performs several deterministic transformations between the manifest contract and the point event contract.

Key responsibilities include:

- mapping synthetic IDs to event IDs
- deriving elapsed time
- converting raw fields into schema-compliant structure
- removing manifest-only fields (e.g., `replay_order`)

The synthetic identifier mapping step ensures that event records have stable, event-oriented identifiers appropriate for Kafka publication. Elapsed time derivation provides time-based context that may not exist in a directly consumable form in the raw manifest. Structural conversion adapts source fields into the exact layout required by `contracts/point_event_schema.json`.

The producer also removes fields that are useful only for replay execution but should not appear in the outward-facing event contract. For example, `replay_order` is needed to control replay sequencing, but it is not part of the point event schema and must not be leaked into downstream payloads.

This transformation layer is therefore both additive and restrictive: it derives needed output values while also filtering out fields that would violate the outbound contract.

---

## 7. Dead Letter Queue (DLQ)

Invalid events are routed to:

- `tennis.point.events.dlq`

The DLQ is used to isolate records that cannot be safely published to the primary event stream.

Types of failures:

- manifest validation errors
- point event schema violations

Each DLQ message contains:

- error type
- error message
- raw event

This structure makes the DLQ operationally useful. The error type allows quick classification of failure modes. The error message provides immediate diagnostic context. The raw event preserves the original payload for debugging, replay investigation, or remediation workflows.

Using a DLQ instead of dropping bad records silently is an important reliability measure. It protects the integrity of the main topic while preserving visibility into data quality issues.

---

## 8. Kafka Topics

The replay producer uses the following Kafka topics:

| Topic | Purpose |
|------|--------|
| `tennis.point.events` | Valid point events |
| `tennis.point.events.dlq` | Invalid events |
| `tennis.replay.audit` | Audit and monitoring |

The primary event topic carries only validated, schema-compliant point events. The DLQ provides containment for invalid data. The audit topic supports observability by allowing monitoring systems or operators to inspect producer behavior, replay progress, and validation outcomes.

This topic separation keeps operational concerns distinct from business-event delivery and makes monitoring easier to reason about.

---

## 9. Testing Strategy

The testing approach covers both unit-level contract checks and end-to-end Kafka validation.

### Unit Tests

- `test_kafka_event_contract.py`
  - validates event schema compliance
- `test_replay_producer.py`
  - verifies transformation logic
  - ensures no invalid fields are included

The unit tests are designed to verify the producer's core correctness properties in isolation. Schema tests confirm that generated events conform to the defined point event contract. Transformation tests verify that source fields are mapped correctly, derived values are generated as expected, and manifest-only fields do not leak into outbound messages.

### Integration Testing

- Producer executed with `--limit` for controlled testing
- Kafka consumer used to verify published messages
- Validation consumer confirms schema compliance

Integration testing validates the full execution path from manifest read to Kafka publication. Running the producer with `--limit` makes the test deterministic and easier to inspect. A Kafka consumer confirms that messages are actually published to the expected topic, while a validation consumer verifies that published payloads remain schema-compliant in a live flow rather than only in isolated unit tests.

---

## 10. Results

Test run with 20 events:

- Events produced: 20
- Valid events: 20
- Invalid events: 0
- DLQ messages: 0

These results indicate that, for the evaluated sample, the replay producer completed the full pipeline without contract violations or routing failures. Every produced event passed validation, and no records required DLQ handling.

---

## 11. Observations

- Missing optional fields (e.g., surface, rally length) are handled as `null`
- System is resilient to partial data
- Schema enforcement ensures downstream reliability

The handling of optional fields is an important design characteristic. By representing absent optional values as `null`, the producer preserves schema consistency without inventing data. This allows downstream systems to distinguish between "unknown or unavailable" and "present with a value."

The producer also appears resilient to partial input records as long as required fields remain valid. Combined with strict schema enforcement, this supports a reliable stream contract for downstream analytics and processing services.

---

## 12. Conclusion

The replay producer successfully:

- enforces strict schema contracts
- ensures reliable Kafka event production
- handles invalid data safely via DLQ
- provides a scalable foundation for real-time streaming analytics

Based on the audit scope and test evidence provided, the replay producer is operating as a well-structured contract-enforcement layer between curated replay data and Kafka-based downstream consumers. Its validation strategy, transformation discipline, and DLQ handling provide a strong basis for dependable replay-driven event streaming.
