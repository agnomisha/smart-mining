#include <DHT.h>
#include <math.h>

// ------------------ Pin Definitions ------------------
#define MQ135_PIN A0
#define RL 10000.0   // Load resistance (10k ohm)
float R0 = 20359.54; // Calibrated R0 value

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ADXL335 pins
const int xPin = A1;
const int yPin = A2;
const int zPin = A3;
// Moving Average filter for MQ135
const int N = 10;   // Number of samples for averaging
int mqReadings[N];
int mqIndex = 0;
long mqSum = 0;
float mqAverage = 0;

// ------------------ Setup ------------------
void setup() {
  Serial.begin(9600);
  dht.begin();

  Serial.println("Multi-Sensor System Starting...");
  Serial.print("Using fixed R0 = ");
  Serial.println(R0);
}

// ------------------ Main Loop ------------------
void loop() {
  // -------- MQ135 Gas Sensor --------
  float Rs = getSensorResistance();
  float ratio = Rs / R0;
  

  float ppm_log = (-0.42) * log10(ratio) + 2.8357; 
  float ppm = pow(10, ppm_log);

  Serial.print("CO₂: ");
  Serial.print(ppm);
  Serial.println(" ppm");

  // -------- DHT11 Sensor --------
 /**/ float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("DHT11 reading failed!");
    return; // skip loop if failed
  }

  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.print(" °C | Humidity: ");
  Serial.print(hum);
  Serial.println(" %");

  // -------- ADXL335 Accelerometer --------
  int xRaw = analogRead(xPin);
  int yRaw = analogRead(yPin);
  int zRaw = analogRead(zPin);

  // Convert to voltage
  float xVolts = (xRaw / 1023.0) * 5.0;
  float yVolts = (yRaw / 1023.0) * 5.0;
  float zVolts = (zRaw / 1023.0) * 5.0;

  // Convert to acceleration in g (assuming 0g=1.65V, sensitivity ~0.3V/g)
  float xAcc = (xVolts - 1.65) / 0.3;
  float yAcc = (yVolts - 1.65) / 0.3;
  float zAcc = (zVolts - 1.65) / 0.3;

  float accelMag = sqrt((xAcc * xAcc) + (yAcc * yAcc) + (zAcc * zAcc));

  Serial.print("Accel (g): X=");
  Serial.print(xAcc);
  Serial.print(" | Y=");
  Serial.print(yAcc);
  Serial.print(" | Z=");
  Serial.print(zAcc);
  Serial.print(" | Magnitude=");
  Serial.println(accelMag);


  delay(10000); // update every 5 seconds
}

// ------------------ Functions ------------------
// Calculate sensor resistance for MQ135
float getSensorResistance() {
  int adcValue = analogRead(MQ135_PIN);
  // Moving Average
  mqSum = mqSum - mqReadings[mqIndex];
  mqReadings[mqIndex] = adcValue;
  mqSum = mqSum + mqReadings[mqIndex];
  mqIndex = (mqIndex + 1) % N;
  mqAverage = (float)mqSum / N;

  float voltage = (mqAverage / 1023.0) * 5.0;
  if (voltage == 0) voltage = 0.0001; // avoid div/0
  float Rs = (5.0 - voltage) * RL / voltage;
  return Rs;
}
