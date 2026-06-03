## Lambda Consumer — Working (03-Jun-2026)

Pipeline confirmed working end to end:
Simulator -> Kinesis -> Lambda -> S3

What I observed:

- trigger state was Enabled but showing "No records processed"
- Reason: trigger uses LATEST position - only reads NEW records
- After running simulator: S3 immediately populated with JSON files
- Path structure: raw/year=2026/month=06/day=03/Machine-XX/timestamp.json

Key understanding:

- Lambda is event-driven. I never called it. Kinesis called it automatically.
- base64.b64decode() is mandatory - Kinesis always encodes data
- Date partitioning in S3 path enables Athena partition pruning later
- Each file = one sensor reading = one row in future analytics table

DEA-C01 skills covered:

- Skill 1.1.7: Call Lambda from Kinesis - DONE with real working code
- Skill 1.2.5: Implement transformation services - Lambda as lightweight transform

## Glue ETL — Working (03-Jun-2026)

What I built:
Glue job reads raw JSON from S3, validates, enriches with temp_category,
converts to Parquet, partitions by machine_id and ingestion_date

What I observed in S3:
processed/machine_id=Machine-01/ingestion_date=2026-06-03/part-00000.snappy.parquet

Key learnings:

- .snappy.parquet = Parquet format + Snappy compression
- partitionBy creates folder structure Athena uses for partition pruning
- part-00000, part-00010, part-00023 = multiple Spark workers writing in parallel
- job.commit() saves the Job Bookmark - next run only processes new files
- temp_category column added: CRITICAL/HIGH/NORMAL/LOW - enrichment at ETL layer

Why Parquet over JSON:

- JSON: one file per record, ~168 bytes each, row-based
- Parquet: columnar, compressed, many records per file, 80% smaller
- Athena query cost: Parquet scans only columns you query, not all columns

DEA-C01 skills covered:

- Skill 1.2.5: Implement transformation services (Glue) - DONE
- Skill 1.2.6: Transform between formats JSON to Parquet - DONE
- Skill 1.2.4: Cost optimisation through Parquet and partitioning - DONE
