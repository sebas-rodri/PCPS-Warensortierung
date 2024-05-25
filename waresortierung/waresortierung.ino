#include <WiFiS3.h>
#include "communication.h"
const float MAX_WEIGHT = 500;

unsigned int NR_BOXES;
float THRESHOLD;
int *boxes_array;

WiFiUDP Udp;

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
  //boxes_array = (unsigned int*)malloc(NR_BOXES * sizeof(int));
  if(boxes_array == NULL) {
    // error handeling
    exitFunction(); 
  }

  // initialization with 0
  for(int i = 0; i < NR_BOXES; i++){ boxes_array[i] = 0; }
  return;
}

// setup code to run once:
void setup() {
  //NR_BOXES initialisieren
  //THRESHOLD initialisieren
  
  initializingArray();

  // Waage
  // Lichtschranke
  // LED
}

/**
 * send a message to Raspberry
 * 
 * @param message is the message to send
 */
 // to implement
void sendMessage(String message) {
  
}

/**
 * read out the scale and handle errors
 * 
 * @returns weight of package
 */
 // to implement
float scale() {
  
}

/**
 * sorting the package into the right box (Box 0 with least weight)
 * 
 * @param weight is the weight of the package to be sorted
 * @returns number of box or -1 on error
 */
int sort(float weight) { 
  if (weight < 0 || weight > THRESHOLD) { return -1; }    // Fehlerbehandlung
  if (weight < THESHOLD) { return 0; }                    // Box 0
  return 1;                                               // Box 1
}

/**
 * read out the photoelectric sensor
 * 
 * @return number of full box or -1 if not triggered
 */
int photoelectricSensor() {
  
}

// main code to run repeatedly:
void loop() {
  float weight = scale();
  int witch_box = sort(weight);
  
  String messageWB = String(witch_box);         // convert int to String: message to be send to raspberry
  sendMessage(messageWB);
  
  boxes_array[witch_box]++;                     // increase the counter for the amount of packages in the box

  // warten auf message das roboter ferig ist

  int full_box = photoelectricSensor();
  // if a box is full send the relevant info to raspberry and terminate program
  if(full_box >= 0) {
    String messageFB = String(full_box);
    sendMessage(messageFB);
    exitFunction();
  }
  
}
/**
*Set up for the WIFI uses predefined SSID and Password
*/
int setUpWiFi(){
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to WiFi network:
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
*Sends a UDP Packet with the give command
*/
int sendPacket(char command){
  Serial.println("Send Packet");
  Udp.beginPacket(IPAddress(IP_ADDRESS), PORT);
  Udp.write(command);
  Udp.endPacket();
}

int recvPacket(){

}
