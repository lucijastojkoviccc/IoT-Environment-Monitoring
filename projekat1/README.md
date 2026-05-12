
# Nano Voice Sensor Control

IoT aplikacija razvijena za Arduino Nano 33 BLE Sense uređaj. Sistem koristi Edge Impulse model za prepoznavanje glasovnih komandi "start" i "stop". Nakon komande "start", uređaj aktivira praćenje pokreta pomoću IMU senzora. Kada se detektuje pomeranje uređaja, RGB LED dioda blinka. Komanda "stop" zaustavlja praćenje i gasi LED.

## Hardware
- Arduino Nano 33 BLE Sense
- Built-in PDM microphone
- Built-in IMU sensor
- Built-in RGB LED

## Software
- Arduino IDE
- Edge Impulse
- Arduino_LSM9DS1 library
- Edge Impulse Arduino inferencing library

## Voice commands
- Start: activates movement monitoring
- Stop: deactivates movement monitoring

## Application logic
1. The microphone records audio.
2. Edge Impulse model classifies the command.
3. If "start" is detected above threshold, movement monitoring starts.
4. IMU sensor monitors movement along X, Y and Z axes.
5. If movement is detected, the RGB LED blinks orange.
6. If "stop" is detected, monitoring stops and LED turns off.
