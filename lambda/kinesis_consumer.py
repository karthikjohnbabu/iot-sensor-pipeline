import json, base64, boto3, os
from datetime import datetime, timezone

s3 = boto3.client("s3")
cloudwatch = boto3.client("cloudwatch")
RAW_BUCKET = os.environ.get("S3_RAW_BUCKET", "iot-pipeline-raw-014498643193")

def validate_reading(record):
    required = ["machine_id", "timestamp", "temperature_c",
                "vibration_hz", "pressure_bar"]
    for field in required:
        if field not in record:
            return False, f"Missing field: {field}"
    if not (0 <= record["temperature_c"] <= 200):
        return False, f"Temperature out of range: {record['temperature_c']}"
    if record["vibration_hz"] < 0:
        return False, f"Negative vibration"
    return True, None

def write_to_s3(record, prefix):
    now = datetime.now(timezone.utc)
    machine_id = record.get("machine_id", "unknown")
    key = (f"{prefix}/year={now.year}/month={now.month:02d}/"
           f"day={now.day:02d}/{machine_id}/{now.strftime('%H%M%S%f')}.json")
    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=key,
        Body=json.dumps(record).encode("utf-8"),
        ContentType="application/json"
    )
    return key

def publish_metric(machine_id, temperature):
    cloudwatch.put_metric_data(
        Namespace="IoT/SensorPipeline",
        MetricData=[{
            "MetricName": "MachineTemperature",
            "Dimensions": [{"Name": "MachineId", "Value": machine_id}],
            "Value": temperature,
            "Unit": "None"
        }]
    )

def lambda_handler(event, context):
    valid_count = 0
    invalid_count = 0
    for kinesis_record in event["Records"]:
        payload = base64.b64decode(kinesis_record["kinesis"]["data"])
        record = json.loads(payload.decode("utf-8"))
        is_valid, error = validate_reading(record)
        if is_valid:
            write_to_s3(record, "raw")
            publish_metric(record["machine_id"], record["temperature_c"])
            valid_count += 1
        else:
            record["_error"] = error
            write_to_s3(record, "quarantine")
            invalid_count += 1
            print(f"INVALID: {error}")
    print(f"Processed: {valid_count} valid, {invalid_count} invalid")
    return {"statusCode": 200, "valid": valid_count, "invalid": invalid_count}