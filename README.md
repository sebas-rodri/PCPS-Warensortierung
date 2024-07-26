# Praktikum Warensortierung

> A project for the Cyber-Physical Systems project at TU Berlin.

This project automates goods reception using a robotic arm. Packages are classified by weight and sorted by the robotic arm.

## Architecture
Learn more in the [WIKI](https://github.com/sebas-rodri/PCPS-Warensortierung/wiki)

## Hardware Requirements

- Wlkata Mirobot 6-Axis Robot Arm
- Raspberry Pi 5
- Arduino Uno R4 WiFi
- Scale
- Light Barrier
- Packages

## Features

- Sorts packages by weight.
- When a package is placed in the goods receiving area (scale), the weight is recorded at the press of a button, and the package is sorted.

## Set Up
1.    WLAN-Router einschalten
2.    LAN-Kabel an Raspberry Pi anschließen
3.    Roboter mit dem Ladekabel verbinden
4.    Roboter an den Raspberry Pi anschlißen
5.    Roboter einschalten
6.    Raspberry Pi an den Strom anschließen
7.    PC mit planthubwifi W-LAN verbinden und in Bash `shh team@raspberrypi.local` eingeben (Passwort: hallo)
8.    `bash setup.sh` in Bash ausführen (bei Fehlermeldung zehn Sekunden warten und ab Schritt 6 wieder ausführen)
9.    Alle Pakete aus allen Boxen und von der Waage entfernen (Waage muss frei sein)
10.   Arduino einschalten 
11.   Überprüfen, ob die Lichtschranken nicht blockiert sind und auf den Wiederstand leuchten. Falls Laser nicht auf die Wiederstände leuchten, vorsichtig zurecht biegen
12.   Im Browser "http://192.168.1.105:4999" aufrufen

## Bedienung des Programms
1.    Ein Packet in die Einabebox legen (bitte nicht mehr als eins).
2.    "Pick up" zum Sortieren klicken (dabei ist drauf zu achten, dass sich keine Pakete auf der Waage befinden).
3.    Wenn die Lichtschranke blockiert ist (angezeigt auf der Webseite), Box lehren und Packete von der Waage entfernen. Bei Schritt 1 wieder anfangen.
