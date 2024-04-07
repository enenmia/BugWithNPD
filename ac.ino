int yellowLedPin = 2;
int greenLedPin = 3;
int redLedPin = 4;
bool yellowLedState = false; // 用于跟踪黄色 LED 的当前状态

void setup() {
  pinMode(yellowLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  
  digitalWrite(yellowLedPin, HIGH);
  digitalWrite(greenLedPin, LOW);
  digitalWrite(redLedPin, LOW);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    switch (command) {
      case 'y': // 控制黄色 LED 闪烁
        yellowLedState = !yellowLedState; // 切换 LED 状态
        digitalWrite(yellowLedPin, yellowLedState ? HIGH : LOW);
        delay(500); // 闪烁延时
        break;
      case 'g': // 控制绿色 LED
        digitalWrite(redLedPin, HIGH);
        digitalWrite(greenLedPin, HIGH);
        digitalWrite(yellowLedPin, LOW);
        break;


      // 其他命令处理
    }
  }
}
