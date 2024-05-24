/*
*Communication interface which defines messages for Arduino Wifi Connectivity
*Should be updated with corresponding Python File
*Author: Sebastian Rodriguez
*/
#define RESET		"0"
#define BUCKET_ONE	"1"
#define BUCKET_TWO	"2"
#define SECRET_SSID "Totogolazo"
#define SECRET_PASS ""
#define PORT        2360
#define IP_ADDRESS  "0.0.0.0"



int setUpWiFi();
int sendPacket(char command);
int recvPacket();

