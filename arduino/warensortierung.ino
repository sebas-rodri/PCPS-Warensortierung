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
#define LASER_2 4
#define BUTTON 7
#define SENSITIVITY_LIGHT_BARRIER -100      // Sets the difference in voltage for the light barrier to trigger

/*---- define pins for scale and initializes LoadCell ----*/
const int HX711_dout = 6;                   // mcu > HX711 dout pin
const int HX711_sck = 7;                    // mcu > HX711 sck pin
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eeprom_address = 0;

/*---- initialize global variables ----*/
const float MAX_WEIGHT = 10000;             // maximal weight for the packages
int THRESHOLD;                              // weight threshold for package sorting
int STANDARD_LB = 0;                        // variable for the standard value of the light barrier for one box
int STANDARD_LB_2 = 0;                      // variable for the standard value of the light barrier for other box

/*---- initialize variables needed for Wi-Fi ----*/
char SSID[] = SECRET_SSID;                  // the network SSID (name), see communication.h
char PASS[] = SECRET_PASS;                  // the network password (use for WPA, or use as key for WEP), see communication.h
const char *TCP_SERVER_ADDR = IP_ADDRESS;   // to this IP-address data shall be sent
const int TCP_SERVER_PORT = PORT;           // to this port data shall be sent
IPAddress ip(192, 168, 1, 141);

WiFiServer server(80);                      // initialize TCP server
WiFiClient TCP_client;                      // initialize TCP client

/*____________________ Set-Up Functions ____________________*/

/*!
 * Assembling a string to send to the Raspberry Pi from a message and a weight.
 * @param message is either a number representing a command or a character representing an error message
 * @param weight is the weight of the packet.
 * @return the message and weight assembled into a string. Example: "1/059"
 */
char *assembleData(char message, float weight) {
    int weight_int = (int) weight;                      // cast float to int
    char *result = (char *) malloc(6 * sizeof(char))    // allocate memory for string

    if (weight_int == 0) {                              // if there is no weight
        snprintf(result, 6, "%c/000", message);
    }
    else if (weight_int < 10) {                         // if the weight is less than 2 digits
        snprintf(result, 6, "%c/00%d", message, weight_int);
    }
    else if (weight_int < 100) {                        // if the weight is less than 3 digits
        snprintf(result, 6, "%c/0%d", message, weight_int);
    }
    else {
        snprintf(result, 6, "%c/%d", message, weight_int);
    }

    return result;
}


/*!
 * Set up the Wi-Fi connection via TCP to the Raspberry Pi.
 */
void setUpWiFi() {
    Serial.println("Arduino: TCP CLIENT");

    WiFi.config(ip);

    if (WiFi.status() == WL_NO_MODULE) {            // check for the Wi-Fi module
        Serial.println("Communication with WiFi module failed!");
        /* visual output for error */
        digitalWrite(LED, HIGH);
        delay(5000);
        digitalWrite(LED, LOW);
        exit(0);                                    // on error terminate program
    }

    /*String fv = WiFi.firmwareVersion();
      if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
          Serial.println("Please upgrade the firmware");
      }*/

    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SSID);
    while (WiFi.begin(SSID) != WL_CONNECTED) {      // attempt to connect to Wi-Fi network
        delay(10000);                               // wait 10 seconds for connection and try again
    }
    Serial.print("Connected to WiFi ");
    Serial.println(SSID);

    server.begin();

    if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {     // connect to TCP server
        Serial.println("Connected to TCP server");
        TCP_client.write("0/000");                                  // send a reset command to TCP Server
        TCP_client.flush();
    } else {
        Serial.println("Failed to connect to TCP server");          // in case of failure the program tries again before sending data in sendData
    }
    //Serial.println(WiFi.localIP());
}


/*!
 * Start up the scale
 */
void startupScale() {
    LoadCell.begin();
    //LoadCell.setReverseOutput();      // turn a negative output value to positive
    float calibration_value;            // calibration value (see example file "Calibration.ino")
    calibration_value = -974.2;         // set the calibration value in the sketch

    //#if defined(ESP8266) || defined(ESP32)
    //    EEPROM.begin(512);                                      // uncomment this to use ESP8266/ESP32 and fetch the calibration value from eeprom
    //#endif
    //    EEPROM.get(calVal_eeprom_address, calibration_value);   // fetch the calibration value from eeprom

    unsigned long stabilizing_time = 2000;          // precision right after power-up can be improved by adding a few seconds of stabilizing time
    boolean _tare = true;                           // set false to skip tare in the next step
    LoadCell.start(stabilizing_time, _tare);

    if (LoadCell.getTareTimeoutFlag()) {            // if start up failed
        sendData("s/000");                          // send scale error to Raspberry Pi
        TCP_client.stop();
        exit(0);                                    // exit program
    }
    else {
        LoadCell.setCalFactor(calibration_value);   // else, set calibration value (float)
        Serial.println("Startup is complete");
    }
}

/*!
 * This code runs once on start up of the Arduino. The sensors are declared, all set up functions are called and the LED blinks to indicate completed set up.
 */
void setup() {
    Serial.begin(9600);             // Setup for testing with serial port(9600)
    Serial.print("test begin\n");

    /* initialize the sensors*/
    pinMode(BUTTON, INPUT);
    pinMode(LED, OUTPUT);
    pinMode(LASER, OUTPUT);
    pinMode(LASER_2, OUTPUT);
    pinMode(LIGHT_BARRIER, INPUT);
    pinMode(LIGHT_BARRIER_2, INPUT);
    STANDARD_LB = analogRead(LIGHT_BARRIER);
    STANDARD_LB_2 = analogRead(LIGHT_BARRIER_2);
    digitalWrite(LASER, HIGH);
    digitalWrite(LASER_2, HIGH);

    /* start further necessities */
    setUpWiFi();
    startupScale();
}


/*____________________ LOOP Functions ____________________*/

/*!
 * Reads out the scale.
 * @return weight on the scale in gram.
 */
float scale() {
    while (!LoadCell.update()) {}           // wait for scale output
    float weight = LoadCell.getData();
    //Serial.println(weight);
    return weight;
}


/*!
 * Checks the light barriers. If a barrier is blocked, send the appropriate message to the Raspberry Pi and listen for further instruction.
 */
void lightBarrier() {
    /* checks first light barrier */
    if ((STANDARD_LB - analogRead(LIGHT_BARRIER)) >= SENSITIVITY_LIGHT_BARRIER) {
        sendData("l/000");
        loop();
    }
    /* checks second light barrier */
    if ((STANDARD_LB_2 - analogRead(LIGHT_BARRIER_2)) >= SENSITIVITY_LIGHT_BARRIER) {
        sendData("L/000");
        loop();
    }
}


/*!
  * sorting the package into the right box (Box 1 with least weight)
  * @return number of box (1 or 2) or terminates program with error
  */
char sorting() {
    /* read out the scale 20 times to get the right weight */
    for (int i = 0; i <= 20; i++) {
        Serial.println(scale());
        delay(50);
    }

    float weight = scale();                     // read out the scale

    /* error handling */
    if (weight <= 0 || weight > MAX_WEIGHT) {
        sendData("w/000");                      // send error message to Raspberry Pi and listen for further instruction
        loop();
    }
    /* actual sorting */
    if (weight < THRESHOLD) { return '1'; }     // Box 1
    return '2';                                 // Box 2
}


/*!
 * Declare the threshold for sorting the packages.
 * @param message is the sting from which the threshold is to be read.
 */
void assignThreshold(char *message) {
    char weight_str[4];
    weight_str[3] = '\0';
    for (int i = 0; i < 3; i++) {       // copy threshold from message to own string
        weight_str[i] = message[i + 2];
    }
    THRESHOLD = atoi(weight_str);       // convert string to integer
}


/*!
 * Send Data over TCP connection to Raspberry Pi.
 * @param message is the data to be send.
 */
void sendData(char *message) {
    if (!TCP_client.connected()) {
        Serial.println("Connection is disconnected");
        TCP_client.stop();

        if (TCP_client.connect(TCP_SERVER_ADDR, TCP_SERVER_PORT)) {     // reconnect to TCP server
            Serial.println("Reconnected to TCP server");
            TCP_client.write("0/000");                                  // send reset command to TCP server
            TCP_client.flush();
        }
        else {                                                          // on error exit program
            Serial.println("Failed to reconnect to TCP server");

            /* visual output for error */
            digitalWrite(LED, HIGH);
            delay(5000);
            digitalWrite(LED, LOW);
            exit(0);
        }
    }

    TCP_client.write(message);                                          // send to TCP Server (Raspberry Pi)
    free(message);
    TCP_client.flush();
}


/*!
 * Listen for incoming connection requests on port 80 and receive messages.
 */
void receiveData() {
    char message[6] = "9/999";                  // set message string to empty (no valid command)
    message[5] = '\0';

    WiFiClient client = server.available();     // listen for connection
    if (client.available() > 0) {               // when data is received
        for (int i = 0; i < 6; i++) {           // read out first six bytes received into message string
            char thisChar = client.read();
            message[i] = thisChar;
        }
        Serial.print("a:");
        Serial.println(message);
    }
    handleRequest(message);                     // handle the command received
}

/*!
 * Decipher the message received from Raspberry Pi. Handle requests accordingly.
 */
void handleRequest(char *message) {
    if (message[0] == '5') {            // if threshold is to be assigned
        assignThreshold(message);       // assign threshold
        loop();                         // and listen for further instructions
    }
    else if (message[0] == '4') {                            // if a packet is on the scale
        lightBarrier();                                      // check the light barrier
        char *message_1 = assembleData(sorting(), scale());  // if no boxes is full, sort the package and assemble string to send to Raspberry Pi with relevant information
        sendData(message_1);
        loop();                                              // go back to listening for Requests
    }
}


/*!
 * After the start up, this is the function that's actually run. It runs on a loop.
 */
void loop() {
    receiveData();
}
