#include <WiFiS3.h>
#include "communication.h"
#include <SoftwareSerial.h>
#include "Ultrasonic.h"
#include <HX711_ADC.h>

#if defined(ESP8266) || defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif
/* Definition for sensor connections slots */
#define LIGHT_BARRIER A0
#define LED 10
#define LASER 2
#define BUTTON 3
// Sets the difference in voltage for the light barrier to trigger
#define SENSITIVITY_LIGHT_BARRIER -100
// define pins for scale and initializes LoadCell
const int HX711_dout = 4;  // mcu > HX711 dout pin
const int HX711_sck = 5;   // mcu > HX711 sck pin
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const int calVal_eeprom_address = 0;
unsigned long t = 0;

// initialize global variables

//maximal weight for the packages
const float MAX_WEIGHT = 500;
// weight threshold for package sorting
float THRESHOLD;
// number of boxes
unsigned int NR_BOXES = 1;
// array for storing the amount of packages
int *boxes_array;
//Variable for the standard value of the light barrier
int standard_lb = 0;
//variable for the box status
int full_box = -1;

/*-----Initializing Variable for WIFI--------*/
char ssid[] = SECRET_SSID;  // your network SSID (name)
char pass[] = SECRET_PASS;  // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;
WiFiUDP Udp;

/*-----------------------*/

/**
 * orderly shut down of the entire system
 */
// to implement
void exitFunction() {
}

/**
 * initializing an array of boxes where the number of packages per box are counted.
 */
void initializingArray() {
    // declaration
    boxes_array = (int *) malloc(NR_BOXES * sizeof(int));
    // error handling
    if (boxes_array == NULL) {
        exitFunction();
    }

    // initialization with 0
    for (int i = 0; i < NR_BOXES; i++) { boxes_array[i] = 0; }
    return;
}

// setup code to run once:
void setup() {
    // Setup for testing with serial port(9600)
    Serial.begin(9600);
    Serial.print("test begin\n");

    /* initialize the sensors*/
    pinMode(BUTTON, INPUT);
    pinMode(LED, OUTPUT);
    pinMode(LASER, OUTPUT);
    pinMode(LIGHT_BARRIER, INPUT);
    standard_lb = analogRead(LIGHT_BARRIER);
    digitalWrite(LASER, HIGH);

    // start up scale
    startup_Scale();

    // init NR_BOXES
    // init THRESHOLD
    initializingArray();

    //visual output for Startup
    digitalWrite(LED, HIGH);
    delay(5000);
    digitalWrite(LED, LOW);
}


/**
 * setup the scale for measurements
 * 
 * @param none is the message to send
 */
void startup_Scale() {
    LoadCell.begin();
    //LoadCell.setReverseOutput(); //uncomment to turn a negative output value to positive
    float calibration_value;  // calibration value (see example file "Calibration.ino")
    //calibration_value = 887.24; // uncomment to set the calibration value in the sketch
#if defined(ESP8266) || defined(ESP32)
    EEPROM.begin(512);  // uncomment this to use ESP8266/ESP32 and fetch the calibration value from eeprom
#endif
    EEPROM.get(calVal_eeprom_address, calibration_value);  // fetch the calibration value from eeprom
    unsigned long stabilizing_time = 2000;               // precision right after power-up can be improved by adding a few seconds of stabilizing time
    boolean _tare = true;                               // set false to skip tare in the next step
    LoadCell.start(stabilizing_time, _tare);
    if (LoadCell.getTareTimeoutFlag()) {
        Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
        while (1);
    } else {
        LoadCell.setCalFactor(calibration_value);  // set calibration value (float)
        Serial.println("Startup is complete");
    }

}


/**
 * read out the scale and handle errors
 * 
 * @returns weight of package
 */
// to implement
float scale() {
    while (!LoadCell.update()) {}  // wait for scale output
    float weight = LoadCell.getData();
    //Serial.println(weight); // test scale weight
    return weight;
}

/**
 * sorting the package into the right box (Box 0 with least weight)
 * 
 * @param weight is the weight of the package to be sorted
 * @returns number of box or -1 on error
 */
int sort(float weight) {
    if (weight < 0 || weight > THRESHOLD) { exitFunction(); }  // error handling
    if (weight < THRESHOLD) { return 0; }                      // Box 0
    return 1;                                                  // Box 1
}

/**
 * read out the photoelectric sensor
 * 
 * @return -1 if triggered and 1 if not triggered
 */
int light_barrier() {
    if ((standard_lb - analogRead(LIGHT_BARRIER)) < SENSITIVITY_LIGHT_BARRIER) {
        return -1;
    } else {
        return 0;
    }
}

// main code to run repeatedly:
void loop() {

    // checks the light barrier and exits the function if triggered
    if (light_barrier() < 0) {
        exitFunction();
    }
    // sorting package and sending instructions to robot
    sendPacket(byte(sorting()));
}


/**
* function sorting the package and updating package count
* return 1 = box_1 return 2 = box_2
*/
int sorting() {
    float weight = scale();
    int witch_box = sort(weight);
    boxes_array[witch_box]++;  // increase the counter for the amount of packages in the box
    return witch_box;
}


/**
* Set up for the WIFI uses predefined SSID and Password
*/
int setUpWiFi() {
    Serial.begin(9600);
    while (!Serial) { ;  // wait for serial port to connect. Needed for native USB port only
    }

    // check for the Wi-Fi module:
    if (WiFi.status() == WL_NO_MODULE) {
        Serial.println("Communication with WiFi module failed!");
        // don't continue
        while (true);
    }

    String fv = WiFi.firmwareVersion();
    if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
        Serial.println("Please upgrade the firmware");
    }

    // attempt to connect to Wi-Fi network:
    while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(ssid, pass);

        // wait 10 seconds for connection:
        delay(10000);
    }
    Serial.println("Connected to WiFi");
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());

    // print your board's IP address:
    IPAddress ip = WiFi.localIP();
    Serial.print("IP Address: ");
    Serial.println(ip);

    // print the received signal strength:
    long rssi = WiFi.RSSI();
    Serial.print("signal strength (RSSI):");
    Serial.print(rssi);
    Serial.println(" dBm");

    Serial.println("\nStarting connection to server...");
    // if you get a connection, report back via serial:
    Udp.begin(PORT);
}

/**
* @param command is the parameter to sends a UDP Packet with the give command
*/

int sendPacket(byte command) {
    Serial.println("Send Packet");
    if (!Udp.beginPacket(IPAddress(IP_ADDRESS), PORT)) {
        Serial.println("Problem Udp.beginPacket");
    }

    Udp.write(command);


    if (!Udp.endPacket()) {
        Serial.println("The packet wasn't send.");
    }
    Serial.println(command);
}

/**
* Receive UDP Packet from Raspberry Pi (TODO)
*/
int recvPacket() {
}
