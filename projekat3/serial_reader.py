import serial
import paho.mqtt.client as mqtt

# SERIAL

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

# MQTT

MQTT_BROKER = "192.168.0.33"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

# MQTT CLIENT

mqtt_client = mqtt.Client()

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# SERIAL CONNECTION

ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

print("Serial connected")

# MAIN LOOP

while True:

    try:

        line = ser.readline().decode("utf-8").strip()

        if line:

            print("FROM ARDUINO:")
            print(line)

            mqtt_client.publish(MQTT_TOPIC, line)

            print("PUBLISHED TO MQTT")
            print()

    except Exception as e:

        print("ERROR:", e)
