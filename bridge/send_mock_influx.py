import os
from datetime import datetime
import random
import time
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# ==== FILL THESE IN WITH YOUR REAL VALUES ====
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN") 
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
# =============================================


def main():
    # Create client and write API (synchronous is fine for testing)
    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
    )
    write_api = client.write_api()

    print("Writing mock data to Influx... Ctrl+C to stop.")
    try:
        while True:
            # Imagine this dict comes from your UART parser
            data = {
                "id": random.randint(1, 5),
                "yaw": random.uniform(-180, 180),
                "pitch": random.uniform(-90, 90),
                "roll": random.uniform(-180, 180),
            }

            # Build a point for measurement "uart_data"
            point = (
                Point("uart_data")
                .tag("id", str(data["id"]))       # tags = dimensions/grouping
                .field("yaw", float(data["yaw"])) # fields = numeric values
                .field("pitch", float(data["pitch"]))
                .field("roll", float(data["roll"]))
                .time(datetime.utcnow(), WritePrecision.NS)
            )

            # Write to bucket
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

            print("Wrote:", data)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        client.close()


if __name__ == "__main__":
    main()

