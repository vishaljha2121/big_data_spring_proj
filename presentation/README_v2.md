# CourtIQ Final Presentation v2

## Files

- `CourtIQ_Final_Presentation_v2.pptx`: polished 18-slide final deck.
- `speaker_notes_v2.md`: slide-by-slide talk track.
- `assets_v2/diagrams/`: redesigned PNG diagrams and Mermaid sources.
- `assets_v2/screenshots/`: captured dashboard/API screenshots plus manual checklist.

## Regenerate

```bash
.venv/bin/python presentation/build_presentation_v2.py
```

## Screenshot Notes

Real screenshots captured in this environment:

- `assets_v2/screenshots/dashboard_overview.png`
- `assets_v2/screenshots/fastapi_docs.png`

## Evidence Used

- Data validation reports under `data/features/` and `data/results/`
- Kafka runtime reports under `data/results/kafka_runtime/`
- Spark streaming reports under `data/results/spark_streaming/`
- Model evaluation reports under `data/results/model_eval/`
- API/frontend validation reports under `data/results/api_validation/` and `data/results/frontend_validation/`
