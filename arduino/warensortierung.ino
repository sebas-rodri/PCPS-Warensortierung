#include <WiFiS3.h>
#include "communication.h"
#include <SoftwareSerial.h>
#include "Ultrasonic.h"
#include <HX711_ADC.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

/*---- define sensor connections slots ----*/
#define LIGHT_BARRIER A4
#define LIGHT_BARRIER_2 A5
#define LED 10
#define LASER 2
#define BUTTON 7
#define SENSITIVITY_LIGHT_BARRIER -100  // Sets the difference in voltage for the light barrier to trigger

/*---- define pins for scale and initializes LoadCell ----*/
const int HX711_dout = 6;  // mcu > HX711 dout pin
const int HX711_sck = 7;   // mcu > HX711 sck pin
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eeprom_address = 0;
unsigned long t = 0;

/*---- initialize global variables ----*/
const float MAX_WEIGHT = 10000;  // maximal weight for the packages
float THRESHOLD = 20;            // weight threshold for package sorting
unsigned int NR_BOXES = 1;       // number of boxes
int* boxes_array;                // array for storing the amount of packages
int standard_lb = 0;             // variable for the standard value of the light barrier for one box
int standard_lb_2 = 0;           // variable for the standard value of the light barrier for other box
int full_box = -1;               // variable for the box status

/*---- initialize variables needed for Wi-Fi ----*/
char ssid[] = SECRET_SSID;                 // the network SSID (name), see communication.h
char pass[] = SECRET_PASS;                 // the network password (use for WPA, or use as key for WEP), see communication.h
const char* TCP_SERVER_ADDR = IP_ADDRESS;  // to this IP-address data shall be sent
const int TCP_SERVER_PORT = PORT;          // to this port data shall be sent

WiFiClient TCP_client;

/*____________________ Set-Up Functions ____________________*/



/*!
 * Assembling a string to send to the Raspberry Pi from a message and a weight.
 * @param message is either a number representing a command or a character representing an error message
 * @param weight is the weight of the packet. Default 0.0.
 * @return the message and weight assembled into a string.
 */
char* assembleData(char message, float weight) {
  int weight_int = (int)weight;                     // conversion float to int (forgets all decimals, better to round nr?)
  char* result = (char*)malloc(6 * sizeof(char));   // allocating memory for string

  if (weight_int < 100) {                                   // if the weight is less than three digits (weight less than 100g)
    snprintf(result, 6, "%c/0%d", message, weight_int);     // a 0 has to be put in front of the weight (weight in message has to be three digits)
  }
  else {
    snprintf(result, 6, "%c/%d", message, weight_int);
  }

  return result;
}


/*!
 * Orderly shut down of the program including an error message to be sent to the Raspberry Pi.
 * @param error represents the reason for the shut down.
 */
void exitFunction(char error) {
  char* message = assembleData(error, 0.0);
  sendData(message);
  TCP_client.stop();
  exit(0);
}

/*!
 * Set up the Wi-Fi connection via TCP to the Raspberry Pi.
 */
int setUpWiFi() {
  Serial.println("Arduino: TCP CLIENT");

  if (WiFi.status() == WL_NO_MODULE) {                          // check for the Wi-Fi module
    Serial.println("Communication with WiFi module failed!");
    exit(0);                                                    // on error terminate program
  }

  /*String fv = WiFi.firmwareVersion();
    if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
        Serial.println("Please upgrade the firmware");
    }*/

  Serial.print("Attempting to connect to SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid) != WL_CONNECTED) {                    // attempt to connect to Wi-Fi network
    delay(10000);                                               // wait 10 seconds for connection and try again
  }
  Serial.print("Connected to WiFi ");
  Serial.println(ssid);

  if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {   // connect to TCP server
    Serial.println("Connected to TCP server");
    TCP_client.write("Hello!");                                 // send to TCP Server
    TCP_client.flush();
  } else {
    Serial.println("Failed to connect to TCP server");          // in case of failure the program tries again before sending data in sendData
  }
}


/*!
 * Start up the scale
 */
void startup_Scale() {
  LoadCell.begin();
  //LoadCell.setReverseOutput();                          // uncomment to turn a negative output value to positive
  float calibration_value;  // calibration value (see example file "Calibration.ino")
  calibration_value = 800;  // uncomment to set the calibration value in the sketch

  //#if defined(ESP8266) || defined(ESP32)
  //    EEPROM.begin(512);                                      // uncomment this to use ESP8266/ESP32 and fetch the calibration value from eeprom
  //#endif
  //    EEPROM.get(calVal_eeprom_address, calibration_value);   // fetch the calibration value from eeprom

  unsigned long stabilizing_time = 2000;  // precision right after power-up can be improved by adding a few seconds of stabilizing time
  boolean _tare = true;                   // set false to skip tare in the next step
  LoadCell.start(stabilizing_time, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    exitFunction('s');
  } else {
    LoadCell.setCalFactor(calibration_value);  // set calibration value (float)
    Serial.println("Startup is complete");
  }
}

/*!
 * This code runs once on start up of the Arduino. The sensors are declared, all set up functions are called and the LED blinks to indicate completed set up.
 */
void setup() {
  Serial.begin(9600);               // Setup for testing with serial port(9600)
    Serial.print("test begin\n");

  /* initialize the sensors*/
  pinMode(BUTTON, INPUT);
  pinMode(LED, OUTPUT);
  pinMode(LASER, OUTPUT);
  pinMode(LIGHT_BARRIER, INPUT);
  pinMode(LIGHT_BARRIER_2, INPUT);
  standard_lb = analogRead(LIGHT_BARRIER);
  standard_lb_2 = analogRead(LIGHT_BARRIER_2);
  digitalWrite(LASER, HIGH);

  /* start further necessities */
  setUpWiFi();
  startup_Scale();
  // init THRESHOLD with data received from Raspberry Pi

  /* visual output for Startup */
  digitalWrite(LED, HIGH);
  delay(5000);
  digitalWrite(LED, LOW);
}


/*____________________ LOOP Functions ____________________*/

/*!
 * Reads out the scale.
 * @return weight on the scale in gram.
 */
float scale() {
  while (!LoadCell.update()) {}             // wait for scale output
  float weight = LoadCell.getData();
  //Serial.println(weight);                 // test scale weight
  return weight;
}


/*!
 * Checks the light barrier.
 * @return -1 if barrier of box 1 is triggered, -2 for box 2 or 0 if none.
 */
int light_barrier() {
  if ((standard_lb - analogRead(LIGHT_BARRIER)) < SENSITIVITY_LIGHT_BARRIER) {      // checks first light barrier
      return -1;
  }
  if ((standard_lb_2 - analogRead(LIGHT_BARRIER_2)) < SENSITIVITY_LIGHT_BARRIER) {  //checks second light barrier
      return -1;
  }
  return 0;
}


 /*!
  * sorting the package into the right box (Box 1 with least weight)
  * @return number of box (1 or 2) or terminates program with error
  */
char sorting() {
  // ???
  for (int i = 0; i <= 20; i++) {
    Serial.println(scale());
    delay(50);
  }

  float weight = scale();  // figure out weight

  /* actual sorting */
  if (weight < 0 || weight > MAX_WEIGHT) { exitFunction('w'); }  // error handling
  if (weight < THRESHOLD) { return '1'; }                        // Box 1
  return '2';                                                    // Box 2
}


/*!
 * send Data over TCP connection tp Raspberry Pi
 * @param message
 */
void sendData(char* message) {
  if (!TCP_client.connected()) {
    Serial.println("Connection is disconnected");
    TCP_client.stop();

    if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {     // reconnect to TCP server
      Serial.println("Reconnected to TCP server");
      TCP_client.write("Hello!");                                   // send to TCP Server
      TCP_client.flush();
    } else {
      Serial.println("Failed to reconnect to TCP server");
      delay(1000);
    }
  }

  TCP_client.write(message);  // send to TCP Server
  TCP_client.flush();
}


/*!
 * After the start up, this is the function that's actually run. It runs on a loop.
 */
void loop() {

  if (light_barrier() == -1) {                            // checks the light barrier and exits the function if triggered
    char* message = assembleData(sorting(), scale());     // assemble string to send to Raspberry Pi
    sendData(message);
    digitalWrite(LED, HIGH);                              // LED signal light barrier is blocked (a box is full)
    delay(10000);
    digitalWrite(LED, LOW);

  }
  // error handling noch ausarbeten
  else {
    Serial.println("Lichtschranke blockiert");  //error message
    digitalWrite(LED, HIGH);
    delay(200);
    digitalWrite(LED, LOW);
    digitalWrite(LED, HIGH);
    delay(200);
    digitalWrite(LED, LOW);
    digitalWrite(LED, HIGH);
    delay(200);
    digitalWrite(LED, LOW);
  }
}
