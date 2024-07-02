#include <WiFiS3.h>

/*-----Initializing Variable for WIFI--------*/
const char* WIFI_SSID = "planthubwifi";               // CHANGE TO YOUR WIFI SSID
const char* WIFI_PASSWORD = "";                       // CHANGE TO YOUR WIFI PASSWORD
const char* TCP_SERVER_ADDR = "141.23.214.82";        // CHANGE TO TCP SERVER'S IP ADDRESS
const int TCP_SERVER_PORT = 37777;

WiFiClient TCP_client;

/**
 * orderly shut down of the entire system and sending of error messages
 */
void exitFunction(char error) {
    // send error message to raspi
    Serial.println(error);
    //free(boxes_array);
    exit(0);
}

/**
 * Set up for the WIFI uses predefined SSID and Password
 */
int setUpWiFi() {
    Serial.println("Arduino: TCP CLIENT");

    // check for the WiFi module:
    if (WiFi.status() == WL_NO_MODULE) { exitFunction('i'); }

    String fv = WiFi.firmwareVersion();
    if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
        Serial.println("Please upgrade the firmware");
    }

    Serial.print("Attempting to connect to SSID: ");
    Serial.println(WIFI_SSID);
    // attempt to connect to WiFi network:
    while (WiFi.begin(WIFI_SSID, WIFI_PASSWORD) != WL_CONNECTED) {
        delay(10000);  // wait 10 seconds for connection
    }

    Serial.print("Connected to WiFi ");
    Serial.println(WIFI_SSID);

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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);                         // Setup for testing with serial port(9600)
  Serial.print("test begin\n");

  setUpWiFi();
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
 * write data received from RaspberryPi to message string
 *
 * @return message as string received from RaspberryPi
 */
char* recvData() {
    int MSG_LENGTH = 5;
    char* message = new char[MSG_LENGTH];
    for(int i = 0; i < MSG_LENGTH; i++){
        if (TCP_client.available()) {
            char c = TCP_client.read();
            message[i] = c;
        }
        else { break; } // error handling?
    }
    return message;
}

void loop() {
  // put your main code here, to run repeatedly:
  for(int i = 0; i < 1; i++){
    sendData("Hallo"); 
  }
}
