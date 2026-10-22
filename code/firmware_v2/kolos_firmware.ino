// KOLOS, вторая версия программы макета.
// Основа та же, что в первой версии: в течение окна как можно чаще читаем датчик,
// запоминаем минимум и максимум и считаем амплитуду.
// Добавлены RMS, калибровка по фону, порог, подсчёт событий и статус.

const int SENSOR_PIN = 34;
const unsigned long WINDOW_MS = 250;       // длина окна
const unsigned long CALIBRATION_MS = 10000;
const float K = 1.25;                      // порог = 1,25 * фоновый RMS
const int HISTORY = 20;                    // окон в буфере событий
const int ATTENTION_MIN = 3;               // 0-2 события: NORMAL, 3-7: ATTENTION
const int ALERT_MIN = 8;                   // 8 и более: ALERT

bool history[HISTORY];
int pos = 0;
float baseline = 0;
float threshold = 0;

void readWindow(int &amplitude, float &rms) {
  int minimum = 4095;
  int maximum = 0;
  uint64_t sum = 0, sumSq = 0;
  uint32_t n = 0;
  unsigned long start = millis();

  while (millis() - start < WINDOW_MS) {
    int value = analogRead(SENSOR_PIN);
    if (value < minimum) minimum = value;
    if (value > maximum) maximum = value;
    sum += value;
    sumSq += (uint64_t)value * value;
    n++;
  }

  double mean = (double)sum / n;
  double variance = (double)sumSq / n - mean * mean;
  if (variance < 0) variance = 0;
  amplitude = maximum - minimum;
  rms = sqrt(variance);
}

void calibrate() {
  Serial.println("\nCALIBRATION: do not touch the probe for 10 seconds.");
  float total = 0;
  int windows = 0;
  unsigned long start = millis();
  while (millis() - start < CALIBRATION_MS) {
    int amplitude;
    float rms;
    readWindow(amplitude, rms);
    total += rms;
    windows++;
    Serial.print(".");
  }
  baseline = total / windows;
  threshold = K * baseline;
  for (int i = 0; i < HISTORY; i++) history[i] = false;
  Serial.println("\nCALIBRATION COMPLETE");
  Serial.printf("Baseline RMS: %.1f\nDetection threshold: %.1f\n\n", baseline, threshold);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(SENSOR_PIN, ADC_11db);
  delay(500);
  calibrate();
}

void loop() {
  int amplitude;
  float rms;
  readWindow(amplitude, rms);

  history[pos] = rms > threshold;
  pos = (pos + 1) % HISTORY;
  int events = 0;
  for (int i = 0; i < HISTORY; i++) events += history[i];

  // ACTIVITY: 50% на пороге, 100% при RMS в 1,5 раза выше фона
  int activity = constrain((int)round(200.0 * (rms / baseline - 1.0)), 0, 100);
  const char *status = events >= ALERT_MIN ? "ALERT" : events >= ATTENTION_MIN ? "ATTENTION" : "NORMAL";

  Serial.printf("AMP: %d  RMS: %.1f  ACTIVITY: %d%%  EVENTS: %d/%d  STATUS: %s\n",
                amplitude, rms, activity, events, HISTORY, status);

  // 'c' в Serial Monitor: повторная калибровка
  if (Serial.available() && Serial.read() == 'c') calibrate();
}
