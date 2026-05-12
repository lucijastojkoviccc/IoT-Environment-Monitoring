import json
import time
import numpy as np
import paho.mqtt.client as mqtt

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883

INPUT_TOPIC = "sensors/nano"
OUTPUT_TOPIC = "actuators/light_alert"

MODEL_PATH = "light_model.tflite"

CLASS_NAMES = {
    0: "dark",
    1: "normal",
    2: "bright",
    3: "anomaly"
}

previous_prediction = None

print("Starting TFLite ML service - UPDATED VERSION WITH MESSAGES...", flush=True)

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def classify_light(brightness, contrast):
    input_data = np.array(
        [[brightness / 255.0, contrast / 255.0]],
        dtype=np.float32
    )

    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]["index"])[0]
    predicted_class = int(np.argmax(output_data))
    confidence = float(np.max(output_data))

    return CLASS_NAMES[predicted_class], confidence


def build_action_message(prediction):
    if prediction == "anomaly":
        return (
            "SECURITY_ALERT_TRIGGERED",
            "Unusual light pattern detected. The system would activate a warning indicator and notify the monitoring dashboard."
        )

    if prediction == "dark":
        return (
            "ADAPTIVE_LIGHTING_INCREASE",
            "Low ambient light detected. The system would increase room lighting to restore optimal visibility."
        )

    if prediction == "bright":
        return (
            "ADAPTIVE_LIGHTING_DECREASE",
            "Excessive light exposure detected. The system would reduce lighting or adjust blinds to prevent overexposure."
        )

    return (
        "ENVIRONMENT_STABLE",
        "Ambient lighting is within the expected range. No corrective action is required."
    )

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker. Code: {reason_code}", flush=True)
    client.subscribe(INPUT_TOPIC)
    print(f"Subscribed to topic: {INPUT_TOPIC}", flush=True)


def on_message(client, userdata, msg):
    global previous_prediction

    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        brightness = float(data.get("brightness", 0))
        contrast = float(data.get("contrast", 0))

        prediction, confidence = classify_light(brightness, contrast)

        action, message = build_action_message(prediction)

        if previous_prediction is None:
            state_changed = False
            change_message = f"Initial state detected: {prediction}."
        elif prediction != previous_prediction:
            state_changed = True
            change_message = f"State changed from {previous_prediction} to {prediction}."
        else:
            state_changed = False
            change_message = f"State unchanged: {prediction}."

        previous_prediction = prediction

        result = {
            "brightness": brightness,
            "contrast": contrast,
            "prediction": prediction,
            "confidence": confidence,
            "state_changed": state_changed,
            "message": message,
            "change_message": change_message,
            "action": action
        }

        client.publish(OUTPUT_TOPIC, json.dumps(result))

        print("ML result:", result, flush=True)

    except Exception as e:
        print(f"Error in ML service: {e}", flush=True)


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
        time.sleep(5)
