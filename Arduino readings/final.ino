const int CSn1 = 12;
const int DO1 = 13;

const int CSn2 = 5;
const int DO2 = 4;

const int CLK = 8;

const int OFFSET1 = 3219;
const int OFFSET2 = 6372;

void setup() {
  Serial.begin(9600);

  pinMode(CSn1, OUTPUT);
  pinMode(DO1, INPUT);

  pinMode(CSn2, OUTPUT);
  pinMode(DO2, INPUT);

  pinMode(CLK, OUTPUT);

  digitalWrite(CLK, HIGH);
  digitalWrite(CSn1, HIGH);
  digitalWrite(CSn2, HIGH);
}

void loop() {
  unsigned int raw1 = readSensor(CSn1, DO1);
  delayMicroseconds(1);
  unsigned int raw2 = readSensor(CSn2, DO2);
  delayMicroseconds(1);

  float degrees1 = convertToDegrees(raw1, OFFSET1);
  float degrees2 = convertToDegrees(raw2, OFFSET2);

  Serial.print("Encoder 1: ");
  Serial.print(degrees1);
  Serial.print("\t");

  Serial.print("Encoder 2: ");
  Serial.print(degrees2);
  Serial.println(" ");

  delay(100); // Just for readability in Serial Monitor
}

unsigned int readSensor(int CSn_pin, int DO_pin) {
  unsigned int dataOut = 0;

  digitalWrite(CSn_pin, LOW);
  delayMicroseconds(1);

  for (int x = 0; x < 12; x++) {
    digitalWrite(CLK, LOW);
    delayMicroseconds(1);
    digitalWrite(CLK, HIGH);
    delayMicroseconds(1);
    dataOut = (dataOut << 1) | digitalRead(DO_pin);
  }

  digitalWrite(CSn_pin, HIGH);
  return dataOut;
}

// Convert encoder value to degrees based on offset
float convertToDegrees(unsigned int val, unsigned int offset) {
  unsigned int adjusted;

  if (val >= offset) {
    adjusted = val - offset;
  } else {
    adjusted = 4096 + val - offset;
  }

  return (adjusted * 360.0) / 4096.0;
}
