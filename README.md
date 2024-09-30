# Fuzzy Logic with Raspberry Pi 4 for Sensor Data Collection

This project demonstrates how to use fuzzy logic for decision-making with data collected by sensors connected to a Raspberry Pi 4. The sensor data is processed and uploaded based on specific metrics such as temperature, humidity, and light intensity, with decisions being made using a fuzzy logic algorithm.

## Project Overview

The Raspberry Pi 4 acts as the core of the system, collecting data from various connected sensors. This data is fed into a fuzzy logic system, which determines how and when to upload the data based on predefined metrics and rules. Fuzzy logic helps handle uncertainties and imprecisions in sensor data for more reliable decision-making.

## Requirements

- **Raspberry Pi 4** (with Raspbian OS installed)
- **Sensors** (e.g., DHT11 for temperature and humidity, LDR for light)
- **Python 3.x**
- **Fuzzy Logic Library**: [skfuzzy](https://scikit-fuzzy.github.io/) (for fuzzy logic processing)
- **Internet connection** (for uploading data to a server or cloud)
  
### Python Libraries

Install required Python libraries with:

```bash
pip install RPi.GPIO adafruit-circuitpython-dht skfuzzy
```
## Setup

### 1. Connect Sensors to Raspberry Pi:
- Attach the temperature/humidity sensor (DHT11/DHT22) to a GPIO pin.
- Connect additional sensors like light or pressure sensors as needed.

### 2. Define Fuzzy Logic Rules:
- Implement fuzzy logic rules using `skfuzzy`. For example:

```python
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

# Define fuzzy variables for temperature and humidity
temp = ctrl.Antecedent(np.arange(0, 41, 1), 'temperature')
hum = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')

# Define fuzzy output for decision (e.g., upload frequency)
upload_freq = ctrl.Consequent(np.arange(0, 11, 1), 'upload_freq')

# Fuzzy rules (example: if temperature is high and humidity is low, upload more frequently)
rule1 = ctrl.Rule(temp['high'] & hum['low'], upload_freq['high'])...
```

### 3. Collect and Process Data:
Use Python to read data from the sensors.
```python
import Adafruit_DHT
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, pin)
```
### 4. Upload Data:
Based on the fuzzy decision, upload sensor data to a server or cloud endpoint.
```python

import requests
data = {'temperature': temperature, 'humidity': humidity}
requests.post('https://your-server.com/upload', json=data)
```
## Usage

Run the Python script to start collecting sensor data and applying fuzzy logic for decision-making.
bash

```python
Process.py
```
The script will process sensor data, apply fuzzy logic rules, and upload data to a server when necessary.
## License

This project is licensed under the MIT License. See the LICENSE file for more details.
