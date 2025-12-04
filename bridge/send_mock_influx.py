import os
import time
import random
from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from dotenv import load_dotenv

# Load env vars from ../.env (adjust path if needed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(ENV_PATH)

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# How often to send data (seconds)
SAMPLE_PERIOD = 0.1   # 10 Hz

# Just to tag this run in Influx
RUN_ID = os.getenv("RUN_ID", "test_001")


def generate_mock_sample():
    """
    Generate one mock telemetry sample.

    Ranges:
      - pressure:        0-1600 psi
      - battery_voltage: 0-12 V
      - steering:       -180-180 deg
      - accelerator_1:   0-100 %
      - accelerator_2:   0-100 %
      - currents:        0-200 A
    """

    pressure = random.uniform(0, 1600)
    battery_voltage = random.uniform(10.5, 12.6)  # bias to "realistic" range
    steering = random.uniform(-180, 180)
    accelerator_1 = random.uniform(0, 100)
    # Accelerator 2 following 1 closely (+/- 3%)
    accelerator_2 = max(0.0, min(100.0, accelerator_1 + random.uniform(-3, 3)))

    current_1 = random.uniform(0, 200)
    current_2 = random.uniform(0, 200)
    current_3 = random.uniform(0, 200)
    current_4 = random.uniform(0, 200)

    return {
        "pressure": pressure,
        "battery_voltage": battery_voltage,
        "steering": steering,
        "accelerator_1": accelerator_1,
        "accelerator_2": accelerator_2,
        "current_1": current_1,
        "current_2": current_2,
        "current_3": current_3,
        "current_4": current_4,
    }


def build_point(sample: dict) -> Point:
    """
    Convert the dict into an InfluxDB Point.
    """
    p = (
        Point("vehicle_telemetry")
        .tag("source", "mock")
        .tag("run_id", RUN_ID)
        .field("pressure", float(sample["pressure"]))
        .field("battery_voltage", float(sample["battery_voltage"]))
        .field("steering", float(sample["steering"]))
        .field("accelerator_1", float(sample["accelerator_1"]))
        .field("accelerator_2", float(sample["accelerator_2"]))
        .field("current_1", float(sample["current_1"]))
        .field("current_2", float(sample["current_2"]))
        .field("current_3", float(sample["current_3"]))
        .field("current_4", float(sample["current_4"]))
        .time(datetime.utcnow(), WritePrecision.NS)
    )
    return p


def main():
    if not INFLUX_TOKEN or not INFLUX_ORG or not INFLUX_BUCKET:
        raise RuntimeError("Missing INFLUX_TOKEN / INFLUX_ORG / INFLUX_BUCKET in .env")

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api()

    print(f"Writing mock telemetry to {INFLUX_BUCKET} (org={INFLUX_ORG}) at {SAMPLE_PERIOD:.3f}s period")
    print(f"Run ID: {RUN_ID}")
    try:
        while True:
            sample = generate_mock_sample()
            point = build_point(sample)
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"[{datetime.utcnow().isoformat()}] {sample}")
            time.sleep(SAMPLE_PERIOD)
    except KeyboardInterrupt:
        print("\nStopping mock generator.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
