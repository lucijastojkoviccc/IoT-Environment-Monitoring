import json
import time
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPICS =["sensors/nano","actuators/light_alert"]

INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "my-token"
INFLUX_ORG = "ubicomp"
INFLUX_BUCKET = "proj2"

print("Starting MQTT to InfluxDB service...", flush=True)

influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker. Code: {reason_code}", flush=True)

    for topic in MQTT_TOPICS:
        client.subscribe(topic)
        print(f"Subscribed to topic: {topic}", flush=True)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Received MQTT message on {msg.topic}: {payload}", flush=True)

        data = json.loads(payload)

        if msg.topic == "sensors/nano":
            point = (
                Point("camera_monitoring")
                .field("brightness", float(data.get("brightness", 0)))
                .field("min_brightness", int(data.get("min_brightness", 0)))
                .field("max_brightness", int(data.get("max_brightness", 0)))
                .field("contrast", float(data.get("contrast", 0)))
                .tag("light_state", str(data.get("light_state", "unknown")))
                .tag("event_state", str(data.get("event_state", "unknown")))
            )

            write_api.write(
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG,
                record=point
            )

            print("Written camera data to InfluxDB successfully.", flush=True)

        elif msg.topic == "actuators/light_alert":
            prediction_map = {
                "dark": 0,
                "normal": 1,
                "bright": 2,
                "anomaly": 3
            }

            point = (
                Point("ml_predictions")
                .field("prediction_value", prediction_map.get(str(data.get("prediction", "normal")), 1))
                .field("confidence", float(data.get("confidence", 0)))
                .field("state_changed", int(bool(data.get("state_changed", False))))
                .tag("prediction", str(data.get("prediction", "unknown")))
                .tag("action", str(data.get("action", "none")))
                .tag("message", str(data.get("message", "")))
                .tag("change_message", str(data.get("change_message", "")))
            )

            write_api.write(
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG,
                record=point
            )

            print("Written ML prediction to InfluxDB successfully.", flush=True)

        else:
            print(f"Ignored topic: {msg.topic}", flush=True)

    except Exception as e:
        print(f"Error while processing message: {e}", flush=True)

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

while True:
    try:
        print("Connecting to MQTT broker...", flush=True)
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT connection error: {e}", flush=True)
        print("Retrying in 5 seconds...", flush=True)
        time.sleep(5)
