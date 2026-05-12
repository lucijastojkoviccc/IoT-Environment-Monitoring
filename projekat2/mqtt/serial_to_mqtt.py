import serial
import json
import paho.mqtt.client as mqtt

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/nano"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

print("Reading serial data...")

while True:

    line = ser.readline().decode().strip()

    print("RAW:", line)

    try:
        brightness, min_b, max_b, contrast, light_state, event_state = line.split(",")

        payload = {
            "brightness": float(brightness),
            "min_brightness": int(min_b),
            "max_brightness": int(max_b),
            "contrast": float(contrast),
            "light_state": light_state,
            "event_state": event_state
        }

        client.publish(MQTT_TOPIC, json.dumps(payload))

        print("MQTT:", payload)

    except Exception as e:
        print("ERROR:", e)
