#define SECRET_SSID "planthubwifi"
#define SECRET_PASS "WdBKADGBDRxefs6"

/*
*Communication interface which defines messages for Arduino Wifi Connectivity
*Should be updated with corresponding Python File
*Author: Sebastian Rodriguez
*/
#define RESET        (byte)0
#define BUCKET_ONE    (byte)1
#define BUCKET_TWO    (byte)2
#define PORT        2360
#define IP_ADDRESS  "192.168.1.107"


int setUpWiFi();

int sendPacket(byte command);

int recvPacket();