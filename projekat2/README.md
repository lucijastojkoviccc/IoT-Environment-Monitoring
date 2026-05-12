
# IoT Light Monitoring and ML-Based Event Detection System

## Overview

This project presents a distributed IoT system for real-time monitoring and classification of ambient lighting conditions using an Arduino Nano 33 BLE device, an OV7675 camera module, TensorFlow Lite, MQTT communication, InfluxDB, and Grafana.

The system captures brightness and contrast information from the camera, processes the data through a distributed microservice architecture running on Raspberry Pi, performs machine learning inference using a TensorFlow Lite model, and visualizes the results in Grafana dashboards.

The project demonstrates the integration of:

* IoT devices
* edge computing
* MQTT communication
* Dockerized microservices
* time-series databases
* machine learning inference on embedded systems

---

# System Architecture

```text
Arduino Nano 33 BLE + OV7675 Camera
                │
                ▼
        Serial Communication
                │
                ▼
      serial_reader service
                │
                ▼
         MQTT Broker
           (Mosquitto)
                │
        ┌───────┴────────┐
        ▼                ▼
 mqtt_to_influx     ml_service
        │                │
        ▼                ▼
     InfluxDB      ML predictions
                │
                ▼
             Grafana
```

---

# Hardware Components

| Component                | Purpose                                        |
| ------------------------ | ---------------------------------------------- |
| Arduino Nano 33 BLE      | Edge device for sensor data acquisition        |
| OV7675 Camera Module     | Ambient scene analysis                         |
| Raspberry Pi 4           | Central processing and Docker host             |
| USB Serial Communication | Data transfer between Arduino and Raspberry Pi |

---

# Software Components

| Technology      | Role                     |
| --------------- | ------------------------ |
| Python          | Backend microservices    |
| Docker          | Service containerization |
| Mosquitto MQTT  | Real-time messaging      |
| TensorFlow Lite | ML inference             |
| InfluxDB        | Time-series database     |
| Grafana         | Monitoring dashboard     |

---

# Features

* Real-time brightness and contrast monitoring
* MQTT-based distributed communication
* TensorFlow Lite inference on Raspberry Pi
* Detection of:

  * dark environments
  * bright environments
  * normal lighting conditions
  * anomalies
* Simulated actuator actions
* Grafana dashboard visualization
* Dockerized microservice architecture

---

# Machine Learning Model

The ML model is implemented using TensorFlow/Keras and converted to TensorFlow Lite format for lightweight execution on Raspberry Pi.

## Input Features

* brightness
* contrast

## Output Classes

| Class | Meaning |
| ----- | ------- |
| 0     | dark    |
| 1     | normal  |
| 2     | bright  |
| 3     | anomaly |

---

# Simulated Actuator Actions

| Prediction | Action            |
| ---------- | ----------------- |
| dark       | increase lighting |
| bright     | decrease lighting |
| anomaly    | trigger warning   |
| normal     | no action         |

---



---

# MQTT Topics

| Topic                   | Description                                   |
| ----------------------- | --------------------------------------------- |
| `sensors/nano`          | Raw sensor and camera data                    |
| `actuators/light_alert` | ML predictions and simulated actuator actions |

---

# Docker Services

| Service        | Description                        |
| -------------- | ---------------------------------- |
| serial_reader  | Reads serial data from Arduino     |
| mosquitto      | MQTT broker                        |
| mqtt_to_influx | Writes MQTT data into InfluxDB     |
| ml_service     | Executes TensorFlow Lite inference |
| influxdb       | Stores time-series data            |
| grafana        | Visualizes data                    |

---

# Running the System

## Start all services

```bash
docker compose up -d
```

## Rebuild services

```bash
docker compose up -d --build
```

## View logs

```bash
docker logs -f serial_reader
docker logs -f mqtt_to_influx
docker logs -f ml_service
```

---

# Grafana

Grafana dashboard provides:

* brightness monitoring
* contrast monitoring
* ML prediction visualization
* anomaly detection tracking
* actuator event monitoring

Default Grafana URL:

```text
http://<raspberry-pi-ip>:3000
```

---

# Example ML Output

```json
{
  "brightness": 92.4,
  "contrast": 163.0,
  "prediction": "normal",
  "confidence": 0.93,
  "action": "ENVIRONMENT_STABLE"
}
```

---

# Challenges During Development

* Serial communication setup between Arduino and Raspberry Pi
* Docker orchestration on Raspberry Pi
* TensorFlow Lite compatibility
* MQTT topic synchronization
* ML model calibration
* Real-time event visualization

---

# Future Improvements

* CNN-based image processing
* Full image inference instead of extracted features
* Real actuator integration
* Mobile application support
* Cloud deployment
* Edge AI optimization

---

# Author

Lucija Stojković
Faculty of Electronic Engineering
Master Studies – Software Engineering
