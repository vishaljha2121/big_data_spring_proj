# DEPRECATED PLAN NOTICE: This document is historical and should not be used as the current implementation source of truth. Use README.md, CODEX.md, docs/parallel_workstream_handoff.md, and the current milestone docs instead.

# 14-Day (2-Week) End-to-End Project Execution Plan

> Deprecated planning note: this document is not the current implementation source of truth. It references older Cassandra, Elasticsearch, 50M-record, 25K events/sec, Grafana, and Kibana goals that are not part of the active milestone path. Use `README.md`, `docs/next_implementation_steps.md`, and the current milestone audit documents instead.

This document outlines a high-intensity, detailed 14-day pipeline to fully realize the **Real-Time Tennis Oddsmaking & Integrity Monitoring** Big Data project. Given the complexity of the Lambda Architecture, tasks are heavily parallelized across the team.

---

## **Week 1: Infrastructure, Ingestion, & Batch ML Pipeline**

### **Day 1: Environment Setup & Data Acquisition**
- **Tasks:**
  - Setup Docker Compose environment (Kafka, Spark, Cassandra, Elasticsearch).
  - Download Jeff Sackmann ATP and Point-by-Point datasets.
  - Initialize the Git repository and set up a shared Python/PySpark environment.
- **Deliverable:** Working local cluster with all core services running.

### **Day 2: Kafka Producer & Data Amplification (Ingestion)**
- **Tasks:**
  - Write Python scripts to clean the base CSVs.
  - Develop the Custom Kafka Producer to simulate live match streams concurrently (multithreading/asyncio).
  - Implement the stochastic data inflation logic to generate the 50M-record batch dataset.
- **Deliverable:** 25K events/sec streaming into the `live-points` Kafka topic; 20 GB Parquet archive generated.

### **Day 3: HDFS/S3 Storage & Spark SQL Feature Engineering**
- **Tasks:**
  - Load the synthesized 20 GB Parquet dataset into HDFS/local distributed storage.
  - Implement the PySpark SQL feature extraction pipeline (Rolling windows, serve dynamic features, fatigue proxies).
- **Deliverable:** Fully materialized 120-feature dataset ready for MLlib.

### **Day 4: MLlib Model Training (Live Odds Engine)**
- **Tasks:**
  - Train the **Gradient-Boosted Tree (GBT)** and **Logistic Regression** baseline.
  - Implement 5-fold cross-validation and hyperparameter grid search.
  - Serialize the best-performing model to storage for the streaming layer.
- **Deliverable:** Trained, serialized point-prediction models with AUC metrics.

### **Day 5: Integrity Guardian - Baseline Profiling**
- **Tasks:**
  - Use Spark SQL to compute robust multi-dimensional baseline profiles for all players based on the historical feature dataset.
  - Store player profiles as broadcast variables or in a fast-lookup tier for the streaming layer.
- **Deliverable:** Completed historical baseline profiles.

### **Day 6: Integrity Guardian - Unsupervised ML (Anomaly Detection)**
- **Tasks:**
  - Train the **Isolation Forest** model on the batch feature matrix to detect structural anomalies.
  - Train the **K-Means Clustering** model to define playstyle archetypes.
  - Define the scoring heuristic $\alpha \cdot S_{\text{IsoForest}} + (1 - \alpha) \cdot S_{\text{KMeans}}$.
- **Deliverable:** Serialized anomaly ensemble models.

### **Day 7: Database Schema Design (Serving Layer)**
- **Tasks:**
  - Configure **Cassandra** keyspaces and tables (`live_odds` table partitioned by `match_id`).
  - Configure **Elasticsearch** mappings for integrity alert documents (full-text search optimizing).
- **Deliverable:** Serving layer ready to accept streaming data.

---

## **Week 2: Speed Layer, UI Integration, & Final Deliverables**

### **Day 8: Spark Structured Streaming (Speed Layer) - Core Setup**
- **Tasks:**
  - Connect PySpark Structured Streaming to the `live-points` Kafka topic.
  - Implement 15-point sliding window aggregations on the streaming dataframe.
- **Deliverable:** Real-time rolling aggregates streaming to console.

### **Day 9: Streaming ML Inference & Sink Integration**
- **Tasks:**
  - Load the batch-trained models (GBT & Isolation Forest) into the streaming context.
  - Apply the ML inference to the streaming dataframe (Odds Calculation + Deviation Scoring).
  - Write outputs into Cassandra and Elasticsearch sinks.
- **Deliverable:** Live odds logic populating Cassandra; Suspicious points indexing in Elasticsearch.

### **Day 10: Presentation Layer (Grafana & Kibana)**
- **Tasks:**
  - Connect **Grafana** to Cassandra to visualize live match odds, momentum shifts, and win probabilities.
  - Connect **Kibana** to Elasticsearch, creating dashboards for filtering risk alerts and investigating player anomalies.
- **Deliverable:** Two fully functional operational dashboards.

### **Day 11: System Integration & Stress Testing**
- **Tasks:**
  - Test end-to-end flow: Kafka Producer $\rightarrow$ Spark Streaming $\rightarrow$ DB Sinks $\rightarrow$ UI.
  - Push the Kafka producer to simulate 5,000 concurrent matches ($\sim$25K msgs/sec).
  - Monitor memory, throughput (events/sec), and latency (end-to-end sub-1s goal).
- **Deliverable:** Recorded performance metrics and stability fixes.

### **Day 12: Data Analysis & Visualization Generation**
- **Tasks:**
  - Use Jupyter notebooks connected to Spark to generate static charts: Model validation (ROC curves), cluster distributions, and anomaly case study visualizations.
  - Curate the best structural metrics for the final presentation.
- **Deliverable:** Saved high-quality `.png` charts and tables for the final report.

### **Day 13: Report Authoring (Professional Business Format)**
- **Tasks:**
  - Compile the **Professional-Grade Business Report** (aimed at executive stakeholders).
  - Draft executive summaries, system architecture sections, integration of generated charts, and detailed smart analysis of the sports integrity use case.
- **Deliverable:** Completed PDF report matching professor's rigorous standards.

### **Day 14: Final Review, Slides, & Code Package**
- **Tasks:**
  - Create the presentation slide deck (focusing on business value, big data technologies, and a live or recorded demo).
  - Clean up the codebase, ensure `docker-compose up` runs flawlessly from scratch, and add clear `README.md` instructions.
- **Deliverable:** Final GitHub submission (Code), Presentation Slides, and Final Report. Project Complete!
