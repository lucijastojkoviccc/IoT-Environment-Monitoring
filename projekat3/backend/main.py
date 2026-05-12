from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import paho.mqtt.client as mqtt

from datetime import datetime

import json
import asyncio
import threading

class ActionRequest(BaseModel):

    action: str

class ConfigRequest(BaseModel):

    brightness_threshold: int

    contrast_threshold: int

    sampling_interval: int


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


latest_data = {
    "brightness": 0,
    "contrast": 0,
    "light_state": "unknown",
    "event_state": "unknown",
    "timestamp": ""
}


config = {

    "brightness_threshold": 100,

    "contrast_threshold": 40,

    "sampling_interval": 2
}


history = []

active_connections = []


def on_connect(client, userdata, flags, rc):

    print("Connected to MQTT broker")

    client.subscribe("sensor/data")

    print("SUBSCRIBED TO sensor/data")


def on_message(client, userdata, msg):

    global latest_data

    print("MQTT MESSAGE RECEIVED")

    try:

        payload = json.loads(
            msg.payload.decode()
        )

        brightness = payload["brightness"]

        contrast = payload["contrast"]

        #
        # DYNAMIC CLASSIFICATION
        #

        if brightness < config["brightness_threshold"]:

            light_state = "dark"

        elif brightness > (
            config["brightness_threshold"] + 80
        ):

            light_state = "bright"

        else:

            light_state = "normal"

        #
        # EVENT DETECTION
        #

        if contrast > config["contrast_threshold"]:

            event_state = "high_contrast"

        else:

            event_state = "normal"

        #
        # FINAL DATA
        #

        latest_data = {

            "brightness": brightness,

            "contrast": contrast,

            "light_state": light_state,

            "event_state": event_state,

            "timestamp": str(datetime.now())
        }

        history.append(
            latest_data.copy()
        )

        #
        # LIMIT HISTORY SIZE
        #

        if len(history) > 100:

            history.pop(0)

        print()
        print("NEW MQTT DATA:")
        print(latest_data)

    except Exception as e:

        print("MQTT ERROR:", e)


mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


@app.on_event("startup")
def startup_event():

    print("STARTING MQTT CLIENT")

    def start_mqtt():

        mqtt_client.connect(
            "192.168.0.33",
            1883,
            60
        )

        mqtt_client.loop_forever()

    mqtt_thread = threading.Thread(
        target=start_mqtt
    )

    mqtt_thread.daemon = True

    mqtt_thread.start()

    print("MQTT THREAD STARTED")


@app.get("/")
def root():

    return {

        "message": "IoT Backend Running"
    }


@app.get("/api/latest")
def get_latest():

    return latest_data


@app.get("/api/config")
def get_config():

    return config


@app.post("/api/config")
def update_config(new_config: ConfigRequest):

    config["brightness_threshold"] = \
        new_config.brightness_threshold

    config["contrast_threshold"] = \
        new_config.contrast_threshold

    config["sampling_interval"] = \
        new_config.sampling_interval

    print()
    print("NEW CONFIG:")
    print(config)

    return {

        "message": "Config updated",

        "config": config
    }


@app.get("/api/history")
def get_history():

    return history[-20:]


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    active_connections.append(
        websocket
    )

    print("WebSocket connected")

    try:

        while True:

            await websocket.send_json(
                latest_data
            )

            await asyncio.sleep(1)

    except Exception:

        print("WebSocket disconnected")

        active_connections.remove(
            websocket
        )

@app.post("/api/action")
def send_action(
    action_request: ActionRequest
):

    action = action_request.action

    mqtt_client.publish(
        "sensor/action",
        action
    )

    print()
    print("ACTION SENT:")
    print(action)

    return {

        "message": "Action sent",

        "action": action
    }