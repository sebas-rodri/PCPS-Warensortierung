# Installationsanweisungen

# Arduino

## Benötigt

- PC
- Arduino IDE ([https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)) auf dem PC
- Arduino Uno R4 WiFi
- USB-Kabel

## Installation

1. Öffnen der Arduino IDE
2. Verbinden des Arduino mit PC über USB-Kabel
3. Unter **Tools > Board > Arduino Uno R4 Boards** `Arduino Uno R4 WiFi` Board auswählen
    1. Falls der Arduino Uno R4 WiFi keine Option ist, unter **Tools > Board > Boards Manager** `Arduino Uno R4 Boards` von Arduino installieren
4. Folgende Bibliotheken unter **Sketch > Include Library > Manage Libraries** installieren:
    - `ArduinoBLE` von Arduino
    - `WiFiNINA` von Arduino
    - `HX711_ADC` von Olav Kallhovd
    - `Ultrasonic` von Erick Simoes
5. Lade `warensortierung.ino` unter **Sketch > Upload** oder mit Ctrl+U hoch (achte darauf, dass `communication.h` im gleichen Ordner wie `warensortierung.ino` ist)

# Raspberry Pi

## Benötigt

- PC
- Raspberry Pi 5

## Installation

1. Raspberry Pi an den Strom anschließen
2. Installieren des Raspberry Pi OS. Weitere Informationen dazu: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
3. Verbinden mit dem Raspberry Pi (darauf achten, dass der Raspberry Pi W-Lan hat)
4. Herunterladen von Updates mit `sudo apt update` 
5. Installieren der Updates mit `sudo apt upgrade`
6. Einrichten des apt-Repositorys vom Docker:
    
    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    
    # Add the repository to Apt sources:
    echo \ 
    	"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    	sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    ```
    
7. Installieren der Dockerpakete:
    
    ```bash
    docker login git.tu-berlin.de:5000 gitlab-ci-token $PROJECT_ACCESS_TOKEN
    ```
    
8. Starten beider Docker-Container von dem Registry aus:
    
    ```bash
    docker run -d --network host git.tu-berlin.de:5000/erikh/praktikum-warensortierung/backend
    docker run -d --network host git.tu-berlin.de:5000/erikh/praktikum-warensortierung/webserver
    ```
    
9. Ziehen des Inhalts des Repositorys auf den Desktop:
    
    ```bash
    cd Desktop
    git pull https://git.tu-berlin.de/erikh/praktikum-warensortierung.git
    ```
    
10. Ausführen des handleRequest.py-Skripts im raspi-robot Ordner:
    
    ```bash
    python praktikum-warensortierung/raspi-robot/src/handleRequest.py
    ```