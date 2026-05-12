# IoT Monitoring and Control System

Realtime IoT monitoring and control system built using Arduino Nano 33 BLE Sense, Raspberry Pi 4, FastAPI, MQTT and Android application.

The system performs realtime image-based brightness and contrast analysis using the Arduino camera module, distributes data through MQTT infrastructure and provides live monitoring and remote actuator control through a mobile application.

---

# Features

- Realtime brightness and contrast monitoring
- Distributed IoT architecture
- MQTT communication
- FastAPI backend
- Android mobile application
- WebSocket realtime updates
- Dynamic system configuration
- History tracking
- Remote LED actuator control
- Raspberry Pi edge processing

---

# System Architecture

Arduino Nano 33 BLE Sense
↓ USB Serial
Raspberry Pi 4
↓ MQTT
FastAPI Backend
↓ REST API / WebSocket
Android Application

---

# Hardware Components

| Component | Purpose |
|---|---|
| Arduino Nano 33 BLE Sense | Image processing and sensor data generation |
| OV767X Camera | Grayscale image acquisition |
| Raspberry Pi 4 | Edge device and MQTT bridge |
| Android Phone | Monitoring and control |
| Laptop | FastAPI backend hosting |

---

# Software Technologies

| Technology | Purpose |
|---|---|
| Python | Backend and bridge implementation |
| FastAPI | REST API and WebSocket communication |
| MQTT / Mosquitto | Publish-subscribe messaging |
| PySerial | Serial communication |
| Docker | Service containerization |
| Kotlin | Android application |
| Jetpack Compose | Android UI |
| OkHttp | HTTP and WebSocket client |
| Arduino IDE | Arduino firmware development |

---

# Backend API

## REST Endpoints

| Endpoint | Description |
|---|---|
| `/api/latest` | Latest sensor values |
| `/api/history` | Sensor history |
| `/api/config` | System configuration |
| `/api/action` | Actuator control |

## WebSocket

| Endpoint | Purpose |
|---|---|
| `/ws` | Realtime sensor updates |

---

# Android Application

The Android application contains three main screens:

## Dashboard
- Live sensor values
- Realtime WebSocket updates
- Brightness and contrast visualization

## History
- Realtime history refresh
- Previous sensor readings
- Classification history

## Settings & Control
- Brightness threshold configuration
- Contrast threshold configuration
- Sampling interval configuration
- LED ON/OFF control
- System reset

---

# Raspberry Pi Serial Bridge

The Raspberry Pi acts as an edge bridge between Arduino serial communication and MQTT infrastructure.

Responsibilities:
- Reading serial JSON data
- MQTT publish
- MQTT subscribe
- Sending actuator commands back to Arduino

---

# Dynamic Classification

The backend dynamically classifies lighting conditions based on configurable thresholds received from the Android application.

Possible states:
- dark
- normal
- bright
- high_contrast

---

# Running the System

## 1. Start Docker Services on Raspberry Pi

```bash
docker compose up -d
```

## 2. Start Serial Bridge

```bash
source venv/bin/activate
python serial_bridge.py
```

## 3. Start FastAPI Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. Run Android Application

Run the Android application on a physical Android device connected to the same WiFi network.

---

# Example JSON Payload

```json
{
  "brightness": 123.5,
  "contrast": 145.0,
  "light_state": "normal",
  "event_state": "high_contrast"
}
```

---

# Technical Challenges

- Serial communication between Arduino and Raspberry Pi
- MQTT synchronization
- WebSocket realtime updates
- Android coroutine handling
- Distributed system integration
- Dynamic runtime configuration
- Cross-device communication

---

# Demo Functionality

- Live sensor monitoring
- Realtime dashboard updates
- Dynamic threshold changes
- Live history refresh
- Remote LED control
- Distributed MQTT communication

---

# Author

Lucija Stojković
Faculty of Electronic Engineering
University of Niš
