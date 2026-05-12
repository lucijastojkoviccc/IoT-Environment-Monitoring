#define EIDSP_QUANTIZE_FILTERBANK 0

#include <PDM.h>
#include <Arduino_LSM9DS1.h>
#include <Nano_Voice_Sensor_Control_inferencing.h>

// =====================
// THRESHOLDS
// =====================
float START_THRESHOLD = 0.85;
float STOP_THRESHOLD  = 0.85;
float MOVEMENT_THRESHOLD = 0.20;

// Pauza između dva pokušaja prepoznavanja glasa.
// Ovo NE produžava audio window modela, ali sprečava da stalno prebrzo snima.
const unsigned long VOICE_RECORD_INTERVAL_MS = 2500;

// =====================
// STATE
// =====================
bool monitoringActive = false;
bool blinkingActive = false;

unsigned long blinkStartTime = 0;
unsigned long lastBlinkToggleTime = 0;
unsigned long lastVoiceRecordTime = 0;
unsigned long lastCommandTime = 0;

const unsigned long BLINK_DURATION_MS = 3000;
const unsigned long BLINK_INTERVAL_MS = 250;
const unsigned long COMMAND_COOLDOWN_MS = 2500;

bool ledCurrentlyOn = false;

float baseX = 0.0;
float baseY = 0.0;
float baseZ = 0.0;

// =====================
// AUDIO STRUCT
// =====================
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static signed short sampleBuffer[2048];
static bool debug_nn = false;

// =====================
// FUNCTION DECLARATIONS
// =====================
static bool microphone_inference_start(uint32_t n_samples);
static bool microphone_inference_record(void);
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr);
static void microphone_inference_end(void);
static void pdm_data_ready_inference_callback(void);

void setOrangeLed(bool on);
void turnOffRgbLed();
void updateLedState();
void calibrateMovementBaseline();
void checkMovement();

// =====================
// SETUP
// =====================
void setup()
{
    Serial.begin(115200);
    while (!Serial);

    Serial.println("Voice + IMU Movement Detection Demo");
    Serial.println("-----------------------------------");

    pinMode(LEDR, OUTPUT);
    pinMode(LEDG, OUTPUT);
    pinMode(LEDB, OUTPUT);
    turnOffRgbLed();

    if (!IMU.begin()) {
        Serial.println("ERR: Failed to initialize IMU!");
        while (1);
    }

    Serial.println("IMU initialized.");

    if (microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT) == false) {
        Serial.print("ERR: Could not allocate audio buffer, size: ");
        Serial.println(EI_CLASSIFIER_RAW_SAMPLE_COUNT);
        return;
    }

    Serial.println("Microphone initialized.");
    Serial.println("Say START to turn orange LED ON and activate movement monitoring.");
    Serial.println("Move the device to make the LED blink.");
    Serial.println("Say STOP to turn LED OFF and deactivate monitoring.");
}

// =====================
// LOOP
// =====================
void loop()
{
    updateLedState();

    if (monitoringActive) {
        checkMovement();
    }

    unsigned long now = millis();

    if (now - lastVoiceRecordTime < VOICE_RECORD_INTERVAL_MS) {
        delay(20);
        return;
    }

    lastVoiceRecordTime = now;

    Serial.println();
    Serial.println("Recording voice command...");

    bool ok = microphone_inference_record();
    if (!ok) {
        Serial.println("ERR: Failed to record audio.");
        return;
    }

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;

    ei_impulse_result_t result = { 0 };

    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) {
        Serial.print("ERR: Failed to run classifier: ");
        Serial.println(r);
        return;
    }

    float startScore = 0.0;
    float stopScore = 0.0;

    Serial.println("Predictions:");
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        const char *label = result.classification[ix].label;
        float value = result.classification[ix].value;

        Serial.print("  ");
        Serial.print(label);
        Serial.print(": ");
        Serial.println(value, 5);

        if (strcmp(label, "Start") == 0 || strcmp(label, "start") == 0) {
            startScore = value;
        }
        else if (strcmp(label, "Stop") == 0 || strcmp(label, "stop") == 0) {
            stopScore = value;
        }
    }

    bool cooldownPassed = (millis() - lastCommandTime) > COMMAND_COOLDOWN_MS;

    if (cooldownPassed && startScore >= START_THRESHOLD && startScore > stopScore) {
        monitoringActive = true;
        blinkingActive = false;
        lastCommandTime = millis();

        Serial.println("COMMAND ACCEPTED: START");
        Serial.println("Orange LED ON. Movement monitoring ACTIVE.");

        calibrateMovementBaseline();

        setOrangeLed(true);
    }
    else if (cooldownPassed && stopScore >= STOP_THRESHOLD && stopScore > startScore) {
        monitoringActive = false;
        blinkingActive = false;
        lastCommandTime = millis();

        Serial.println("COMMAND ACCEPTED: STOP");
        Serial.println("LED OFF. Movement monitoring INACTIVE.");

        turnOffRgbLed();
    }
    else {
        Serial.println("No voice command accepted.");
    }

    Serial.print("Monitoring state: ");
    Serial.println(monitoringActive ? "ACTIVE" : "INACTIVE");
}

// =====================
// MOVEMENT LOGIC
// =====================
void calibrateMovementBaseline()
{
    Serial.println("Calibrating baseline position...");

    float sumX = 0.0;
    float sumY = 0.0;
    float sumZ = 0.0;
    int samples = 20;

    for (int i = 0; i < samples; i++) {
        float x, y, z;

        while (!IMU.accelerationAvailable()) {
            updateLedState();
        }

        IMU.readAcceleration(x, y, z);

        sumX += x;
        sumY += y;
        sumZ += z;

        delay(50);
    }

    baseX = sumX / samples;
    baseY = sumY / samples;
    baseZ = sumZ / samples;

    Serial.println("Baseline set:");
    Serial.print("  X: "); Serial.println(baseX);
    Serial.print("  Y: "); Serial.println(baseY);
    Serial.print("  Z: "); Serial.println(baseZ);
}

void checkMovement()
{
    if (!IMU.accelerationAvailable()) {
        return;
    }

    float x, y, z;
    IMU.readAcceleration(x, y, z);

    float diffX = abs(x - baseX);
    float diffY = abs(y - baseY);
    float diffZ = abs(z - baseZ);

    bool movementDetected =
        diffX > MOVEMENT_THRESHOLD ||
        diffY > MOVEMENT_THRESHOLD ||
        diffZ > MOVEMENT_THRESHOLD;

    if (movementDetected && !blinkingActive) {
        Serial.println("MOVEMENT DETECTED!");
        Serial.print("  diffX: "); Serial.println(diffX);
        Serial.print("  diffY: "); Serial.println(diffY);
        Serial.print("  diffZ: "); Serial.println(diffZ);
        Serial.println("Orange LED blinking for 3 seconds.");

        blinkingActive = true;
        blinkStartTime = millis();
        lastBlinkToggleTime = millis();
        ledCurrentlyOn = false;
    }
}

// =====================
// LED LOGIC
// Nano RGB LED je active LOW.
// LOW = ON, HIGH = OFF.
// Orange = Red + Green ON, Blue OFF.
// =====================
void updateLedState()
{
    if (!monitoringActive) {
        turnOffRgbLed();
        return;
    }

    if (blinkingActive) {
        if (millis() - blinkStartTime >= BLINK_DURATION_MS) {
            blinkingActive = false;
            setOrangeLed(true);
            Serial.println("Blink finished. Orange LED steady ON.");
            return;
        }

        if (millis() - lastBlinkToggleTime >= BLINK_INTERVAL_MS) {
            lastBlinkToggleTime = millis();
            ledCurrentlyOn = !ledCurrentlyOn;
            setOrangeLed(ledCurrentlyOn);
        }
    }
    else {
        setOrangeLed(true);
    }
}

void setOrangeLed(bool on)
{
    if (on) {
        digitalWrite(LEDR, LOW);
        digitalWrite(LEDG, LOW);
        digitalWrite(LEDB, HIGH);
    } else {
        turnOffRgbLed();
    }
}

void turnOffRgbLed()
{
    digitalWrite(LEDR, HIGH);
    digitalWrite(LEDG, HIGH);
    digitalWrite(LEDB, HIGH);
}

// =====================
// PDM CALLBACK
// =====================
static void pdm_data_ready_inference_callback(void)
{
    int bytesAvailable = PDM.available();
    int bytesRead = PDM.read((char *)&sampleBuffer[0], bytesAvailable);

    if (inference.buf_ready == 0) {
        for (int i = 0; i < (bytesRead >> 1); i++) {
            inference.buffer[inference.buf_count++] = sampleBuffer[i];

            if (inference.buf_count >= inference.n_samples) {
                inference.buf_count = 0;
                inference.buf_ready = 1;
                break;
            }
        }
    }
}

// =====================
// MICROPHONE START
// =====================
static bool microphone_inference_start(uint32_t n_samples)
{
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));

    if (inference.buffer == NULL) {
        return false;
    }

    inference.buf_count = 0;
    inference.n_samples = n_samples;
    inference.buf_ready = 0;

    PDM.onReceive(&pdm_data_ready_inference_callback);
    PDM.setBufferSize(4096);

    if (!PDM.begin(1, EI_CLASSIFIER_FREQUENCY)) {
        Serial.println("Failed to start PDM.");
        microphone_inference_end();
        return false;
    }

    PDM.setGain(127);

    return true;
}

// =====================
// RECORD AUDIO
// =====================
static bool microphone_inference_record(void)
{
    inference.buf_ready = 0;
    inference.buf_count = 0;

    while (inference.buf_ready == 0) {
        updateLedState();
        delay(10);
    }

    return true;
}

// =====================
// GET AUDIO DATA
// =====================
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr)
{
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);
    return 0;
}

// =====================
// END MICROPHONE
// =====================
static void microphone_inference_end(void)
{
    PDM.end();
    free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif