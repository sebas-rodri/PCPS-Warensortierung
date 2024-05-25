# Praktikum Warensortierung



## Set Up
1. For the WiFi connection to work you will need to set up a static local IP adress on the Raspberry Pi, and 
be on **the same Network**

2. Editing Wi-Fi on a Prewritten Card.
To setup a Wi-Fi connection on your headless Raspberry Pi, open the microSD card on your PC. Then create a text file called wpa_supplicant.conf, and place it in the root directory of the microSD card. You will need the following text in the file.
`country=US 
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
scan_ssid=1
ssid="your_wifi_ssid"
psk="your_wifi_password"
}`



## Pflichtenheft



