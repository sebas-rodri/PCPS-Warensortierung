# Praktikum Warensortierung

> A project for the Cyber-Physical Systems project at TU Berlin.

This project automates goods reception using a robotic arm. Packages are classified by weight and sorted by the robotic arm.

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

Certainly! Here's a configuration section that allows you to set up the Python environment using either Conda or `venv`. This will provide users with the flexibility to choose their preferred method.

---

## Configuration

Follow these steps to set up and configure the system:

### 1. Create a Python Virtual Environment

You have two options for setting up the Python environment: using Conda or `venv`.

#### **Option A: Using Conda**

1. **Install Conda**  
   Ensure you have Conda installed on your system. You can download and install it from the [official Conda website](https://docs.conda.io/en/latest/miniconda.html).

2. **Create and Activate the Conda Environment**  
   Navigate to the `raspi` folder and create a new Conda environment with Python 3.9.6:

    ```bash
    cd raspi
    conda create --name warensortierung python=3.9.6
    conda activate warensortierung
    ```

3. **Install Dependencies**  
   Use the `requirements.txt` file to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. **Verify the Installation**  
   Ensure all dependencies are installed correctly by running:

    ```bash
    pip list
    ```

5. **Deactivate the Environment**  
   When done, you can deactivate the Conda environment with:

    ```bash
    conda deactivate
    ```

#### **Option B: Using `venv`**

1. **Install Python 3.9.6**  
   Ensure Python 3.9.6 is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/release/python-396/).

2. **Set Up the Virtual Environment**  
   Navigate to the `raspi` folder and create a new virtual environment:

    ```bash
    cd raspi
    python3 -m venv venv
    ```

3. **Activate the Virtual Environment**  

    ```bash
    source venv/bin/activate
    ```


4. **Install Dependencies**  
   Use the `requirements.txt` file to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

5. **Verify the Installation**  
   Ensure all dependencies are installed correctly by running:

    ```bash
    pip list
    ```

6. **Deactivate the Environment**  
   When done, you can deactivate the virtual environment with:

    ```bash
    deactivate
    ```

### 2. Set Up Automatic Script Execution

Add `handleRequest.py` to the `rc.local` file on the Raspberry Pi to ensure it runs automatically at startup. Open the `rc.local` file with a text editor:

```bash
sudo nano /etc/rc.local
```

Before the line `exit 0`, add the appropriate command depending on your Python environment setup:

#### **For Conda:**

```bash
#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate warensortierung
python3 /path/to/your/raspi/src/handleRequest.py &
```

Replace `/path/to/your/raspi` with the actual path to your `raspi` directory.

#### **For `venv`:**

```bash
source /path/to/your/raspi/venv/bin/activate
python3 /path/to/your/raspi/src/handleRequest.py &
```

Replace `/path/to/your/raspi` with the actual path to your `raspi` directory.

### 3. Flash the Arduino
