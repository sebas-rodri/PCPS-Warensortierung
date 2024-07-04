#define SECRET_SSID "planthubwifi"
#define SECRET_PASS "WdBKADGBDRxefs6"

/*
 * Communication interface which defines messages for Arduino Wifi Connectivity
 * Should be updated with corresponding Python File
 */
#define RESET         (byte)0
#define BUCKET_ONE    (byte)1
#define BUCKET_TWO    (byte)2

#define SCALE   's'     // scale error: “Timeout, check MCU>HX711 wiring and pin designations”
#define WEIGHT  'w'     // weighting error: package weights too little or too much
#define LIGHT   'l'     // light barrier error: the light barrier was triggered
#define WIFI    'i'     // internet error: “Communication with WiFi module failed”
#define TCP     't'     // server error: “Failed to connect to TCP server”

#define PORT          2360
#define IP_ADDRESS    "192.168.1.147" // anpassen


int setUpWiFi();
void sendData(char* message);
char* receiveData();