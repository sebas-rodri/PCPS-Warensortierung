#include <WiFiS3.h>
#include "communication.h"
#include <SoftwareSerial.h>
#include "Ultrasonic.h"

/* Definition for sensor connections slots */
#define Lichtschranke A0
#define LED 10
#define Laser 2
// Sets the differenz in Voltag for the lightbarrier to trigger
#define sensitivity_lightbarrier -100





const float MAX_WEIGHT = 500;

unsigned int NR_BOXES;
float THRESHOLD;
int *boxes_array;
//Variable for the stadart value of the lightresistir
int standart_lichtwiederstand = 0;

/*-----WIFI STUFF--------*/
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
  boxes_array = (int *)malloc(NR_BOXES * sizeof(int));
  if (boxes_array == NULL) {
    // error handling
    exitFunction();
  }

  // initialization with 0
  for (int i = 0; i < NR_BOXES; i++) { boxes_array[i] = 0; }
  return;
}

// setup code to run once:
void setup() {
  // Setup for testing with Serialport(9600)
  Serial.begin(9600);
  Serial.print("Testbegin\n");

  /* Initialsierung der Sensoren*/
  pinMode(LED, OUTPUT);
  pinMode(Laser, OUTPUT);
  pinMode(Lichtschranke, INPUT);
  standart_lichtwiederstand = analogRead(Lichtschranke);
  Serial.println(standart_lichtwiederstand);

  digitalWrite(Laser, HIGH);

  //visul output for Startup
  digitalWrite(LED, HIGH);
  delay(5000);
  digitalWrite(LED, LOW);

  //NR_BOXES initialisieren
  //THRESHOLD initialisieren

  initializingArray();
}

int test_light_barrier(){
  for (int i = 0; i <= 69; i++) {
    Serial.println(photoelectricSensor());
    delay(5000);
  }
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
  if (weight < 0 || weight > THRESHOLD) { return -1; }  // Fehlerbehandlung
  if (weight < THRESHOLD) { return 0; }                 // Box 0
  return 1;                                             // Box 1
}

/**
 * read out the photoelectric sensor
 * 
 * @return number of full box or -1 if not triggered
 */
int photoelectricSensor() {
  if ((standart_lichtwiederstand - analogRead(Lichtschranke)) < sensitivity_lightbarrier) {
    return -1;
  } else {
    return 0;
  }
}

// main code to run repeatedly:
void loop() {
  float weight = scale();
  int witch_box = sort(weight);

  String messageWB = String(witch_box);  // convert int to String: message to be send to raspberry
  sendMessage(messageWB);

  boxes_array[witch_box]++;  // increase the counter for the amount of packages in the box

  // warten auf message das roboter ferig ist

  int full_box = photoelectricSensor();
  // if a box is full send the relevant info to raspberry and terminate program
  if (full_box >= 0) {
    String messageFB = String(full_box);
    sendMessage(messageFB);
    exitFunction();
  }
}

/**
*Set up for the WIFI uses predefined SSID and Password
*/
int setUpWiFi() {
  Serial.begin(9600);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true)
      ;
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
int sendPacket(byte command) {
  Serial.println("Send Packet");
  if (!Udp.beginPacket(IPAddress(IP_ADDRESS), PORT)) {
    Serial.println("Problem Udp.beginPacket");
  }

  Udp.write(command);


  if (!Udp.endPacket()) {
    Serial.println("The packet wasnt send.");
  }
  Serial.println(command);
}

/**
*Recv UDP Packet from Raspberry Pi (TODO)
*/
int recvPacket() {
}
