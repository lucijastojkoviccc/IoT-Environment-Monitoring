#include <Arduino_OV767X.h>

const int width = 160;
const int height = 120;

uint8_t frame[width * height];

float previousBrightness = 0;

void setup() {
  Serial.begin(115200);

  while (!Serial);

  if (!Camera.begin(QQVGA, GRAYSCALE, 1)) {
    Serial.println("Camera init failed");
    while (1);
  }

  Serial.println("Camera initialized");
}

void loop() {

  Camera.readFrame(frame);

  long sum = 0;

  int minVal = 255;
  int maxVal = 0;

  for (int i = 0; i < width * height; i++) {

    int pixel = frame[i];

    sum += pixel;

    if (pixel < minVal)
      minVal = pixel;

    if (pixel > maxVal)
      maxVal = pixel;
  }

  float brightness = sum / (float)(width * height);

  float contrast = maxVal - minVal;

  String lightState;

  if (brightness < 50)
    lightState = "dark";
  else if (brightness > 180)
    lightState = "bright";
  else
    lightState = "normal";

  String eventState = "normal";

  if (abs(brightness - previousBrightness) > 40)
    eventState = "sudden_change";

  previousBrightness = brightness;

  Serial.print(brightness);
  Serial.print(",");

  Serial.print(minVal);
  Serial.print(",");

  Serial.print(maxVal);
  Serial.print(",");

  Serial.print(contrast);
  Serial.print(",");

  Serial.print(lightState);
  Serial.print(",");

  Serial.println(eventState);

  delay(1000);
}