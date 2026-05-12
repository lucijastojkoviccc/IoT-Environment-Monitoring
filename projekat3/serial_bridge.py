import serial
import json
import time

import paho.mqtt.client as mqtt


#
# SERIAL
#

ser = serial.Serial(

    '/dev/ttyACM0',

    115200,

    timeout=1
)

time.sleep(2)


#
# MQTT
#

broker = "localhost"

mqtt_client = mqtt.Client()


#
# MQTT CALLBACK
#

def on_connect(
    client,
    userdata,
    flags,
    rc
):

    print("Connected to MQTT")

    client.subscribe(
        "sensor/action"
    )

    print(
        "Subscribed to sensor/action"
    )


def on_message(
    client,
    userdata,
    msg
):

    command = msg.payload.decode()

    print()
    print("MQTT COMMAND:")
    print(command)

    #
    # SEND TO ARDUINO
    #

    ser.write(
        f"{command}\n".encode()
    )

    print(
        "COMMAND SENT TO ARDUINO"
    )


mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message


mqtt_client.connect(
    broker,
    1883,
    60
)

mqtt_client.loop_start()


print()
print("STARTING SERIAL READ...")


#
# MAIN LOOP
#

while True:

    try:

        if ser.in_waiting:

            line = ser.readline() \
                .decode() \
                .strip()
            print("RAW:", line)
            #
            # ONLY JSON
            #

            if line.startswith("{"):

                print()
                print("ARDUINO JSON:")
                print(line)

                #
                # VALIDATE JSON
                #

                data = json.loads(line)

                #
                # PUBLISH MQTT
                #

                mqtt_client.publish(
                    "sensor/data",
                    json.dumps(data)
                )

                print(
                    "MQTT PUBLISHED"
                )

    except Exception as e:

        print("ERROR:", e)
