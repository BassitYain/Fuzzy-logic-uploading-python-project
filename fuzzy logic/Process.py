import threading
import time
import numpy as np
import json
from datetime import datetime
import grovepi
import os
import random
import math
import skfuzzy as fuzz
from skfuzzy import control as ctrl

num_readings = 16
max_null_percentage = 10
max_bandwidth = 30
grove_vcc = 5
server_ip = "10.224.2.113"
end_event = threading.Event()

Data = 0
Bandwidth = 0
Energy = 0


# Define functions for each process
def data_sensing():
    # Code for data sensing
    
    # Connect the temperature and humidity sensor to digital port D4
    sensor = 3  # D3

    # Define the number of readings to take
    #num_readings = 50

    # Define the maximum percentage of null values
    #max_null_percentage = 10

    # Create an empty list to store the data
    data_list = []
    global Data 

    # Read data from the sensor
    null_values = 0
    for i in range(num_readings):
        # Read the temperature and humidity values from the sensor
        [temperature, humidity] = grovepi.dht(sensor, 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_list.append({'timestamp': timestamp, 'humidity': humidity, 'temperature': temperature})
        # Check if the data is values
        if np.isnan(humidity) or np.isnan(temperature):
            null_values += 1

        # Wait for 10 second before reading again
        time.sleep(10)

    # Calculate the percentage of null values
    null_percentage = 100.0 * null_values / num_readings

    # Calculate the percentage of data availability excluding the null values
    data_percentage = 100.0 * (num_readings - null_values) / num_readings
    # Convert the data list to a JSON string'''
    json_data = json.dumps(data_list)

    # Write the JSON data to a file
    with open('data.txt', 'w') as file:
        file.write(json_data)

    # Print a message to confirm that the data was written to the file
    print('Data saved to data.txt')
    print (data_list)
    Data = data_percentage
    # Check if the percentage of null values exceeds the maximum allowed
    time.sleep(1)
    return data_percentage
   

def energy_consumption():
    # Set up the ACS725 sensor on analog pin A0
    global Energy
    sensor_pin = 0
    grovepi.pinMode(sensor_pin,"INPUT")

    # Sensor calibration values
    sensor_zero_current = 0    
    sensor_sensitivity = 1000/264   

    # Battery parameters
    #nominal_voltage = 5  # Replace with your battery's nominal voltage
    initial_charge = 2000    # Initial charge of the battery in milliampere-hours
    current_charge = 0.0   # Current charge of the battery in milliampere-hours
    num_readings = 10 
    # Integration variables
    last_time = time.time()
    last_reading = grovepi.analogRead(sensor_pin)

    # Take several readings to calculate the average zero current
    for i in range(num_readings):
        sensor_reading = grovepi.analogRead(sensor_pin)
        sensor_zero_current += sensor_reading

    # Calculate the average zero current
    sensor_zero_current /= num_readings
    # Main loop
    while not end_event.is_set():
        try:
            # Read the sensor value
            sensor_reading = grovepi.analogRead(sensor_pin)
            
            # Convert the sensor value to a current value
            current = (sensor_reading + sensor_zero_current) / sensor_sensitivity

            # Integrate the current value over time
            current_time = time.time()
            dt = current_time - last_time
            charge_delta = current * dt / 3600
            current_charge += charge_delta

            # Print the current and charge values
            print("Current: {:.2f} mA, Charge: {:.2f} mAh".format(current, current_charge))

            # Update integration variables
            last_time = current_time
            last_reading = sensor_reading

            # Wait for a short period before taking the next reading
            time.sleep(0.1)
        except:
            Exception

    # Calculate the final battery capacity
    final_capacity = current_charge
    percentage = ((initial_charge-current_charge)/initial_charge)*100
    Energy = percentage
    # Print the final capacity value
    print("Final capacity: {:.2f} mAh".format(final_capacity))
    print("Battery Percentage: {:.2f} %".format(percentage))
    return percentage




def bandwidth_availability():
    # Code for bandwidth availability   
    #max_bandwidth = 20
    # Replace with your server's IP address
    #server_ip = "10.224.2.113"
    # Run the iperf2 command and get the output
    global Bandwidth
    command = f'iperf -c {server_ip} -i 1 -t 12 -P 7'
    output = os.popen(command).read()
    # Parse the output to get the sent bandwidth
    sent_bandwidth = float(output.split()[-2])
    # Print the sent bandwidth
    #print(f"Sent bandwidth: {sent_bandwidth} Mbits/sec")
    available_bandwidth = 100 * (float(sent_bandwidth) / float(max_bandwidth))
    #print(f'Available bandwidth: {available_bandwidth:.2f}%')
    time.sleep(3)
    Bandwidth = available_bandwidth
    return available_bandwidth
   
        
if __name__ == '__main__':
    # Start the processes
    p1 = threading.Thread(target=data_sensing)
    p2 = threading.Thread(target=energy_consumption)
    p3 = threading.Thread(target=bandwidth_availability)
    
    # Start the processes
    p1.start()
    p2.start()
    # Wait for the processes to complete
    p1_data_availability = p1.join()
    p3.start()
    p3_network_percentage = p3.join()
    # Set the end event to stop the energy consumption process
    end_event.set()
    p2_battery_percentage = p2.join()
   
    # Print the results
    print(f"Data availability: {Data:.2f}%")
    print(f"Battery percentage: {Energy:.2f}%")
    print(f"Network percentage: {Bandwidth:.2f}%")
    
# Input space
energy    = ctrl.Antecedent(np.arange(0, 101, 1), 'energy')
data      = ctrl.Antecedent(np.arange(0, 101, 1), 'data')
bandwidth = ctrl.Antecedent(np.arange(0, 101, 1), 'bandwidth')


# Output space 
offload = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'offload')

# Auto-membership function with .automf(3, 5, or 7)
energy.automf(3)
data.automf(3)
bandwidth.automf(3)

# Custom membership functions can be built interactively 
offload['No'] = fuzz.trapmf(offload.universe, [0, 0, 0.4,0.6])
offload['Yes'] = fuzz.trapmf(offload.universe, [0.4, 0.6,1,1])

energy.view()
data.view()
bandwidth.view()
offload.view()

rule1 = ctrl.Rule(energy['poor'] & bandwidth['poor'] & data['good']    , offload['Yes'])
rule2 = ctrl.Rule(energy['poor'] & bandwidth['poor'] & data['average'] , offload['Yes'])
rule3 = ctrl.Rule(energy['poor'] & bandwidth['poor'] & data['poor']    , offload['Yes'])

rule4 = ctrl.Rule(energy['poor'] & bandwidth['average'] & data['good']    , offload['Yes'])
rule5 = ctrl.Rule(energy['poor'] & bandwidth['average'] & data['average'] , offload['Yes'])
rule6 = ctrl.Rule(energy['poor'] & bandwidth['average'] & data['poor']    , offload['Yes'])

rule7 = ctrl.Rule(energy['poor'] & bandwidth['good'] & data['good']    , offload['Yes'])
rule8 = ctrl.Rule(energy['poor'] & bandwidth['good'] & data['average'] , offload['Yes'])
rule9 = ctrl.Rule(energy['poor'] & bandwidth['good'] & data['poor']    , offload['Yes'])

rule10 = ctrl.Rule(energy['average'] & bandwidth['poor'] & data['good']    , offload['No'])
rule11 = ctrl.Rule(energy['average'] & bandwidth['poor'] & data['average'] , offload['No'])
rule12 = ctrl.Rule(energy['average'] & bandwidth['poor'] & data['poor']    , offload['Yes'])

rule13 = ctrl.Rule(energy['average'] & bandwidth['average'] & data['good']    , offload['No'])
rule14 = ctrl.Rule(energy['average'] & bandwidth['average'] & data['average'] , offload['Yes'])
rule15 = ctrl.Rule(energy['average'] & bandwidth['average'] & data['poor']    , offload['Yes'])

rule16 = ctrl.Rule(energy['average'] & bandwidth['good'] & data['good']    , offload['Yes'])
rule17 = ctrl.Rule(energy['average'] & bandwidth['good'] & data['average'] , offload['Yes'])
rule18 = ctrl.Rule(energy['average'] & bandwidth['good'] & data['poor']    , offload['Yes'])
 
rule19 = ctrl.Rule(energy['good'] & bandwidth['poor'] & data['good']    , offload['No'])
rule20 = ctrl.Rule(energy['good'] & bandwidth['poor'] & data['average'] , offload['No'])
rule21 = ctrl.Rule(energy['good'] & bandwidth['poor'] & data['poor']    , offload['No'])

rule22 = ctrl.Rule(energy['good'] & bandwidth['average'] & data['good']    , offload['No'])
rule23 = ctrl.Rule(energy['good'] & bandwidth['average'] & data['average'] , offload['No'])
rule24 = ctrl.Rule(energy['good'] & bandwidth['average'] & data['poor']    , offload['Yes'])

rule25 = ctrl.Rule(energy['good'] & bandwidth['good'] & data['good']    , offload['No'])
rule26 = ctrl.Rule(energy['good'] & bandwidth['good'] & data['average'] , offload['Yes'])
rule27 = ctrl.Rule(energy['good'] & bandwidth['good'] & data['poor']    , offload['Yes'])
 
offloading_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27])
descision       = ctrl.ControlSystemSimulation(offloading_ctrl)
# Evaluation of the descision table for the different possible scenarios                   
resultat=[]
descision.input['energy'] = Energy
descision.input['data'] = Data
descision.input['bandwidth'] = Bandwidth
descision.compute()
resultat.append(descision.output['offload'])
print(resultat)  
#np.savetxt("resultat_V1.csv",resultat, delimiter=",")
 
# label the descision table values 
op=[]
for i in range (len(resultat)):
    des = ""
    if resultat[i] <= 0.4:
        des = "No"
    if resultat[i] > 0.4 and  resultat[i] <= 0.6 :
        des = "horizontal"
    if resultat[i] > 0.6:
        des = "vertical"
    op.append(des)

brut=[]
for i in range (len(resultat)):
    brut.append("No")
    
print(op)
print(brut)

