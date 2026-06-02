# IoT Sensor Data Pipeline

End-to-end industrial IoT pipeline on AWS: sensor simulation to real-time analytics.

## Architecture

Sensor Simulator -> Kinesis Data Streams -> Lambda -> S3 (raw JSON)
-> Glue ETL -> S3 (Parquet) -> Athena -> CloudWatch Alarms

## Services: Kinesis | Lambda | S3 | Glue | Athena | CloudWatch | EventBridge | SNS

## DEA-C01 Skills

Skill 1.1.1 | 1.1.7 | 1.2.5 | 1.2.6 | 3.3.7

## Setup

pip install boto3 python-dotenv
cp .env.example .env # fill in your values
python3 simulator/sensor_simulator.py
