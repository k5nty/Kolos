const int SENSOR_PIN = 34;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(SENSOR_PIN, ADC_11db);
}

void loop() {
  int minimum = 4095;
  int maximum = 0;

  unsigned long start = millis();

  // Очень быстро считываем датчик в течение 100 мс
  while (millis() - start < 100) {
    int value = analogRead(SENSOR_PIN);

    if (value < minimum) minimum = value;
    if (value > maximum) maximum = value;
  }

  int amplitude = maximum - minimum;

  Serial.print("MIN: ");
  Serial.print(minimum);
  Serial.print("  MAX: ");
  Serial.print(maximum);
  Serial.print("  AMPLITUDE: ");
  Serial.println(amplitude);

  delay(50);
}
