#include <WiFiS3.h>
#include "communication.h"
#include <SoftwareSerial.h>
#include "Ultrasonic.h"
#include <HX711_ADC.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

/*---- Definition for sensor connections slots ----*/
#define LIGHT_BARRIER A4
#define LIGHT_BARRIER_2 A5
#define LED 10
#define LASER 2
#define BUTTON 7
#define SENSITIVITY_LIGHT_BARRIER -100      // Sets the difference in voltage for the light barrier to trigger

/*---- define pins for scale and initializes LoadCell ----*/
const int HX711_dout = 6;  // mcu > HX711 dout pin
const int HX711_sck = 7;   // mcu > HX711 sck pin
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eeprom_address = 0;
unsigned long t = 0;

// initialize global variables

//maximal weight for the packages
const float MAX_WEIGHT = 10000;
// weight threshold for package sorting
float THRESHOLD = 20;
// number of boxes
unsigned int NR_BOXES = 1;
//Variable for the standard value of the light barrier
int standard_lb = 0;
int standard_lb_2 = 0;
//variable for the box status
int full_box = -1;

/*---- Initializing Variable for WIFI ----*/
char ssid[] = SECRET_SSID;                        // your network SSID (name), see communication.h
char pass[] = SECRET_PASS;                        // your network password (use for WPA, or use as key for WEP), see communication.h
const char* TCP_SERVER_ADDR = IP_ADDRESS;         // see communication.h
const int TCP_SERVER_PORT = PORT;

WiFiClient TCP_client;

/*____________________ Set-Up Functions ____________________*/

/**
 * orderly shut down of the entire system and sending of error messages (only after wifi connection is set up)
 */
void exitFunction(char error) {
    // send error message to raspi
    char* message = assembleData(error, 0.0);
    sendData(message);
    TCP_client.stop();
    exit(0);
}

/**
 * Set up for the WIFI uses predefined SSID and Password
 */
int setUpWiFi() {
    Serial.println("Arduino: TCP CLIENT");

    // check for the WiFi module:
    if (WiFi.status() == WL_NO_MODULE) {
      Serial.println("Communication with WiFi module failed!");
      exit(0);                    // on error terminate program
    }

    /*String fv = WiFi.firmwareVersion();
    if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
        Serial.println("Please upgrade the firmware");
    }*/

    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // attempt to connect to WiFi network:
    while (WiFi.begin(ssid) != WL_CONNECTED) {
        delay(10000);  // wait 10 seconds for connection
    }

    Serial.print("Connected to WiFi ");
    Serial.println(ssid);

    // connect to TCP server
    if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {
        Serial.println("Connected to TCP server");
        TCP_client.write("Hello!");  // send to TCP Server
        TCP_client.flush();
    }
    else {
        Serial.println("Failed to connect to TCP server");
    }
}


/**
 * setup the scale for measurements
 */
void startup_Scale() {
    LoadCell.begin();
    //LoadCell.setReverseOutput();                          // uncomment to turn a negative output value to positive
    float calibration_value;                                // calibration value (see example file "Calibration.ino")
    calibration_value = 800;                                // uncomment to set the calibration value in the sketch

    //#if defined(ESP8266) || defined(ESP32)
    //    EEPROM.begin(512);                                      // uncomment this to use ESP8266/ESP32 and fetch the calibration value from eeprom
    //#endif
    //    EEPROM.get(calVal_eeprom_address, calibration_value);   // fetch the calibration value from eeprom

    unsigned long stabilizing_time = 2000;                  // precision right after power-up can be improved by adding a few seconds of stabilizing time
    boolean _tare = true;                                   // set false to skip tare in the next step
    LoadCell.start(stabilizing_time, _tare);
    if (LoadCell.getTareTimeoutFlag()) {
        exitFunction('s');
    }
    else {
        LoadCell.setCalFactor(calibration_value);           // set calibration value (float)
        Serial.println("Startup is complete");
    }


/**
 * setup code to run once:
 */
void setup() {
    // Setup for testing with serial port(9600)
    Serial.begin(9600);
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

    /* start further necesseties */
    setUpWiFi();
    startup_Scale();
    // init THRESHOLD with data received from raspi

    /* visual output for Startup */
    digitalWrite(LED, HIGH);
    delay(5000);
    digitalWrite(LED, LOW);
}


/*____________________ LOOP Functions ____________________*/

/**
 * read out the scale and handle errors
 * 
 * @returns weight of package
 */
float scale() {
    while (!LoadCell.update()) {}           // wait for scale output
    float weight = LoadCell.getData();
    //Serial.println(weight);               // test scale weight
    return weight;
}


/**
 * read out the photoelectric sensor
 * 
 * @return -1 if triggered and 0 if not triggered
 */
int light_barrier() {
  //checks first light barrier
  if ((standard_lb - analogRead(LIGHT_BARRIER)) < SENSITIVITY_LIGHT_BARRIER) {
    return -1;
  }
  //checks second light barrier
  if ((standard_lb_2 - analogRead(LIGHT_BARRIER_2)) < SENSITIVITY_LIGHT_BARRIER) {
    return -1;
  }
  return 0;
}

/**
 * sorting the package into the right box (Box 1 with least weight)
 *
 * @returns number of box (1 or 2) or terminates program with error
 */
char sorting() {
    // ???
    for (int i = 0; i <= 20; i++) {
        Serial.println(scale());
        delay(50);
    }

    float weight = scale();   // figure out weight

    /* actual sorting */
    if (weight < 0 || weight > MAX_WEIGHT) { exitFunction('w'); }   // error handling
    if (weight < THRESHOLD) { return '1'; }                         // Box 1
    return '2';                                                     // Box 2
}

/**
 * assemble data to be send to raspberry pi into string according to specifications
 *
 * @return message to be send as string
 */
char* assembleData(char message, float weight) {
    return "no message";
}


/**
 * send Data over TCP connection tp Raspberry Pi
 * @param message is the message to send
 */
void sendData(char* message) {
    if (!TCP_client.connected()) {
        Serial.println("Connection is disconnected");
        TCP_client.stop();

        // reconnect to TCP server
        if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {
            Serial.println("Reconnected to TCP server");
            TCP_client.write("Hello!");  // send to TCP Server
            TCP_client.flush();
        } else {
            Serial.println("Failed to reconnect to TCP server");
            delay(1000);
        }
    }

    TCP_client.write(message);  // send to TCP Server
    TCP_client.flush();
}


/**
 * main code to run repeatedly:
 */
void loop() {

        // checks the light barrier and exits the function if triggered
        if (light_barrier() == -1) {
            //Serial.println(sorting());
            char* message = assembleData(sorting(), scale());   // assemble string to send to raspberry pi
            sendData(message);
            digitalWrite(LED, HIGH);                  // signal for sending

            delay(10000);
            digitalWrite(LED, LOW);

        }
        // error handeling noch ausarbeten
        else {
            Serial.println("Lichtschranke blockiert");    //error message
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
}