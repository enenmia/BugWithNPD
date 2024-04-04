#define SPEAKER_PIN 10

void setup() {
pinMode(SPEAKER_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
if (Serial.available() > 0) {
    char signal = Serial.read();
    if (signal == '1') {
      digitalWrite(SPEAKER_PIN, HIGH);
      delay(1000);
      digitalWrite(SPEAKER_PIN, LOW);
    }
  } else {
    digitalWrite(SPEAKER_PIN, LOW);
  }
}
