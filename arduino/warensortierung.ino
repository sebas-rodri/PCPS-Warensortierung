#include <WiFiS3.h>
#include "communication.h"
#include <SoftwareSerial.h>
#include "Ultrasonic.h"

/* Definition for sensor connections slots */
#define Lichtschranke A0
#define LED 10
#define Laser 2
#define Button 3
// Sets the differenz in Voltag for the lightbarrier to trigger
#define sensitivity_lightbarrier -100



//Initilasirung globale Variablen

//maximal waight for the packeges
const float MAX_WEIGHT = 500;
// waight threshold for package sorting
float THRESHOLD;
// number of boxes
unsigned int NR_BOXES = 1;
// array for storring the amount of packages
int *boxes_array;
//Variable for the standart value of the lightbarrier
int standart_lb = 0;
//variale for the box status
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
  boxes_array = (int *)malloc(NR_BOXES * sizeof(int));
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
  // Setup for testing with Serialport(9600)
  Serial.begin(9600);
  Serial.print("Testbegin\n");

  /* Initialsierung der Sensoren*/
  pinMode(Button, INPUT);
  pinMode(LED, OUTPUT);
  pinMode(Laser, OUTPUT);
  pinMode(Lichtschranke, INPUT);
  standart_lb = analogRead(Lichtschranke);
  digitalWrite(Laser, HIGH);

  //NR_BOXES initialisieren
  //THRESHOLD initialisieren
  initializingArray();

  //visul output for Startup
  digitalWrite(LED, HIGH);
  delay(5000);
  digitalWrite(LED, LOW);
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
  if (weight < 0 || weight > THRESHOLD) { exitFunction(); }  // Fehlerbehandlung
  if (weight < THRESHOLD) { return 0; }                      // Box 0
  return 1;                                                  // Box 1
}

/**
 * read out the photoelectric sensor
 * 
 * @return -1 if triggered and 1 if not triggered
 */
int lightbarrier() {
  if ((standart_lb - analogRead(Lichtschranke)) < sensitivity_lightbarrier) {
    return -1;
  } else {
    return 0;
  }
}

// main code to run repeatedly:
void loop() {

  // Checks the lightbarrier and exits the funktion if triggert
  if (lightbarrier() < 0) {
    exitFunction();
  }
  //sorting package and sending instrucktions to robot
  sendPacket(byte(sorting()));
}



/**
* funktion sorting the packege and updating package count
* return 1 = box_1 return 2 = box_2
*/
int sorting() {
  float weight = scale();
  int witch_box = sort(weight);
  boxes_array[witch_box]++;  // increase the counter for the amount of packages in the box
  return witch_box;
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
* @param command is the parameter to sends a UDP Packet with the give command
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
