/*
*Communication interface which defines messages for Arduino Wifi Connectivity
*Should be updated with corresponding Python File
*Author: Sebastian Rodriguez
*/

#define RESET		0
#define BUCKET_ONE	1
#define BUCKET_TWO	2

/*CONFIGURE*/
#define SECRET_SSID "Totogolazo" //Config
#define SECRET_PASS ""        //Depends on Router
#define PORT        2360      //Make sure to adress the same Port on Arduino and Python
#define IP_ADDRESS  "0.0.0.0" //Get from Handlerequest.py getLocalIp()
/*------------------------------------------------------------*/



int setUpWiFi();
int sendPacket(byte command);
int recvPacket();

