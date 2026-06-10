# 🏭 IoT Sensor Data Pipeline

> End-to-end industrial IoT data pipeline on AWS — from sensor simulation to real-time analytics and predictive maintenance alerting.

![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?style=flat&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📋 The Problem

A factory has **50 machines**. Each machine has temperature, vibration, and pressure sensors producing readings every second. The operations team needs to know:

- Which machines are running dangerously hot?
- Are there patterns before a machine fails?
- Can we detect anomalies before a breakdown happens?

This pipeline answers all three questions — automatically, in real time, at scale.

---

## 🏗️ Architecture

```
Python Simulator (50 machines × 1 reading/sec)
         │
         │  put_record() — machine_id as partition key
         ▼
Kinesis Data Streams — 5 shards
         │
         │  Event trigger — batch 100, LATEST position
         ▼
Lambda — iot-kinesis-consumer
         │  base64 decode → validate → write to S3 → publish metric
         ▼
S3 Raw Zone
         │  raw/year=2026/month=06/day=03/Machine-XX/timestamp.json
         │  900+ JSON files, date-partitioned
         │
         │  EventBridge triggers hourly
         ▼
Glue ETL — iot-sensor-etl
         │  JSON → Parquet, adds temp_category, Job Bookmarks
         ▼
S3 Processed Zone
         │  processed/machine_id=Machine-XX/ingestion_date=2026-06-03/
         │  186 Parquet files, machine + date partitioned
         │
         │  Glue Crawler → iot_sensor_db catalog
         ▼
Athena — SQL Analytics
         │  5 queries: avg temp, alerts, z-score anomaly, distribution, timeline
         │
         │  Lambda publishes custom CloudWatch metric per reading
         ▼
CloudWatch Alarm — Machine-01-HighTemp
         │  Threshold: MachineTemperature > 85°C within 1 minute
         ▼
SNS — iot-temp-alarm
         │
         ▼
📧 Email alert fired and confirmed ✅
```

---

## ⚙️ AWS Services

| Service                  | Purpose                                                         |
| ------------------------ | --------------------------------------------------------------- |
| **Kinesis Data Streams** | Real-time ingestion, 5 shards, partition by machine_id          |
| **Lambda**               | Event-driven consumer — decode, validate, write, publish metric |
| **S3**                   | Data lake — raw JSON zone and processed Parquet zone            |
| **Glue ETL**             | Batch transform — JSON to Parquet, enrichment, Job Bookmarks    |
| **Glue Crawler**         | Schema discovery — auto-creates table in Glue Data Catalog      |
| **Athena**               | Serverless SQL analytics directly on S3 Parquet files           |
| **CloudWatch**           | Custom metric monitoring and threshold alarm                    |
| **SNS**                  | Email notification when alarm fires                             |
| **EventBridge**          | Hourly schedule trigger for Glue ETL job                        |
| **IAM**                  | Least-privilege roles for Lambda and Glue                       |

---

## 🔑 Key Engineering Decisions

### Why `machine_id` as the Kinesis partition key?

All readings from one machine route to the same shard. This preserves per-machine ordering — essential for time-series anomaly detection.

### Why Parquet instead of JSON?

Parquet is columnar. Athena reads only the columns you query. A query on `temperature_c` with 5 total columns scans 20% of the data instead of 100%. Result: **~80% reduction in Athena query cost**.

### Why partition by `machine_id` and `date`?

Athena skips entire folder partitions that do not match the WHERE clause. A query for Machine-01 today scans 1/50th of the data. Without partitioning, every query scans everything.

### Why Glue Job Bookmarks?

Without bookmarks, every Glue run reprocesses all S3 files and creates duplicates. With bookmarks, each run processes only **new files since the last run**.

### Why a quarantine prefix for invalid records?

Never discard data silently. Invalid readings go to `quarantine/` for investigation. Every record is traceable — valid or invalid.

---

## 📊 Analytics Queries

Five SQL queries in `athena/queries.sql`:

| Query                             | Business Question                                    |
| --------------------------------- | ---------------------------------------------------- |
| Average temperature per machine   | Which machines are running hottest?                  |
| Machines above 85°C               | Which machines need immediate attention?             |
| Z-score anomaly detection         | Which machines show statistically unusual behaviour? |
| Temperature category distribution | What % of readings were CRITICAL vs NORMAL?          |
| Machine-01 timeline               | Full reading history for the anomalous machine       |

---

## 🎓 DEA-C01 Skills Covered

| Skill                                   | Coverage                                         |
| --------------------------------------- | ------------------------------------------------ |
| 1.1.1 Read from streaming sources       | Kinesis producer and consumer built from scratch |
| 1.1.7 Call Lambda from Kinesis          | Event source mapping with batch processing       |
| 1.1.9 Throttling and partition keys     | machine_id partition key design                  |
| 1.1.12 Stateful transactions            | Job Bookmarks track processed files              |
| 1.2.4 Optimise costs                    | Parquet + partitioning = 80% cost reduction      |
| 1.2.5 Implement transformation services | Glue ETL with Spark and enrichment               |
| 1.2.6 Transform between formats         | JSON to Parquet with Snappy compression          |
| 1.2.9 Volume velocity variety           | IoT = high velocity, high volume, structured     |
| 3.2.3 SQL in Athena                     | 5 analytics queries including z-score            |
| 3.3.7 CloudWatch logging                | Custom metric, threshold alarm, SNS              |

---

## 📁 Repository Structure

```
iot-sensor-pipeline/
├── simulator/
│   └── sensor_simulator.py     # 50-machine sensor data producer
├── lambda/
│   └── kinesis_consumer.py     # Decode, validate, write to S3
├── glue/
│   └── etl_job.py              # JSON to Parquet ETL
├── athena/
│   └── queries.sql             # 5 analytics queries
├── docs/
│   └── LEARNING_LOG.md         # Build journal with DEA-C01 connections
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Setup

```bash
# Clone
git clone https://github.com/karthikjohnbabu/iot-sensor-pipeline.git
cd iot-sensor-pipeline

# Virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1

# Dependencies
pip install -r requirements.txt

# AWS credentials
aws configure

# Environment variables
cp .env.example .env
# Edit .env with your AWS account ID
```

---

## 💰 Cost

Total AWS spend for this project: **under $1.00**

> Kinesis costs $0.015/shard/hour. Always delete the stream after each session.
> All other services charge only when actively used.

---

## 👤 Author

**Karthik John Babu**
QA Manager → Data Engineer | AWS DEA-C01 |

- 🐙 GitHub: [karthikjohnbabu](https://github.com/karthikjohnbabu)
- 💼 LinkedIn: [karthik-john-babu](https://www.linkedin.com/in/karthik-john-babu)

---
