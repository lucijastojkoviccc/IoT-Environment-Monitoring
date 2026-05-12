import paho.mqtt.client as mqtt

client = mqtt.Client()

client.connect("192.168.0.33", 1883, 60)

print("CONNECTED")