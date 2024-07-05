#define SECRET_SSID "planthubwifi"
#define SECRET_PASS "WdBKADGBDRxefs6"

/*!
 * Communication interface which defines messages for Arduino Wi-fi Connectivity
 * Should be updated with corresponding Python File
 */
#define RESET         (byte)0
#define BUCKET_ONE    (byte)1
#define BUCKET_TWO    (byte)2

#define SCALE   's'     // scale error: “Timeout, check MCU>HX711 wiring and pin designations”
#define WEIGHT  'w'     // weighting error: package weights too little or too much
#define LIGHT1  'l'     // light barrier error: the light barrier for box 1 was triggered
#define LIGHT2  'L'     // light barrier error: the light barrier for box 2 was triggered

#define PORT          2360
#define IP_ADDRESS    "192.168.1.147" // anpassen


void setUpWiFi();
void sendData(char* message);
char* receiveData();