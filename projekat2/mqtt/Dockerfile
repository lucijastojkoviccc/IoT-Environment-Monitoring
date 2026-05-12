FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY serial_to_mqtt.py .

CMD ["python", "serial_to_mqtt.py"]
