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
