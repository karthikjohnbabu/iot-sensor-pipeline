import boto3, json, time, random, os
from datetime import datetime, timezone
from dotenv import load_dotenv
 
load_dotenv()
 
STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "iot-sensor-stream")
REGION = os.getenv("AWS_REGION", "ap-south-1")
NUM_MACHINES = 50
SEND_INTERVAL_SECONDS = 1
 
kinesis = boto3.client("kinesis", region_name=REGION)
 
def generate_sensor_reading(machine_id):
    machine_num = int(machine_id.split("-")[1])
    base_temp = 60 + (machine_num % 15)
    temperature = base_temp + random.gauss(0, 3)
    if machine_id == "Machine-01" and random.random() < 0.05:
        temperature = random.uniform(87, 95)
    vibration = 50 + (temperature - 60) * 2 + random.gauss(0, 5)
    pressure = random.uniform(98.5, 101.5)
    return {
        "machine_id": machine_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(temperature, 2),
        "vibration_hz": round(max(0, vibration), 2),
        "pressure_bar": round(pressure, 2),
        "status": "ALERT" if temperature > 85 else "NORMAL"
    }
 
def send_to_kinesis(record):
    return kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(record).encode("utf-8"),
        PartitionKey=record["machine_id"]
    )
 
def run_simulator(duration_seconds=60):
    machines = [f"Machine-{i:02d}" for i in range(1, NUM_MACHINES + 1)]
    print(f"Starting: {NUM_MACHINES} machines -> {STREAM_NAME}")
    start = time.time()
    records_sent = 0
    while time.time() - start < duration_seconds:
        cycle_start = time.time()
        for machine_id in machines:
            reading = generate_sensor_reading(machine_id)
            send_to_kinesis(reading)
            records_sent += 1
            if reading["status"] == "ALERT":
                print(f"ALERT: {machine_id} temp={reading['temperature_c']}C")
        elapsed = int(time.time() - start)
        if elapsed % 10 == 0 and elapsed > 0:
            print(f"  {elapsed}s -> {records_sent} records sent")
        sleep_time = max(0, SEND_INTERVAL_SECONDS - (time.time() - cycle_start))
        time.sleep(sleep_time)
    print(f"Done. Sent {records_sent} records in {duration_seconds}s")
 
if __name__ == "__main__":
    run_simulator(duration_seconds=60)
