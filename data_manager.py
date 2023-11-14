#Import csv and data library
import csv
import numpy as np
import os

'''
data manager class
Functionality:
1) Contains code that saves data to csv
2) Contains code to set voltage and current over LAN
'''

class data_manager:

    def __init__(self, inverter_count):
        # ['Ref Voltage'], ['Ref Current'], multiplied by inverter ['Measured Voltage'], ['Measured Current']
        # For mac
        self.save_directory = '/Users/solclarity'
        # For windows
        # self.save_directory = r'C:\Users\bmahabir\Desktop\Calibration CSVs'
        self.vdata_list = []
        self.cdata_list = []
        self.inverter_count = inverter_count

    
    def append_voltages(self, ref_voltages):
        self.vdata_list.append(ref_voltages)
        
    
    def append_currents(self, ref_currents):
        self.cdata_list.append(ref_currents)

    def voltages_to_csv(self):
        #Convert list to numpy
        data_array = np.array(self.vdata_list)

        # Specify the CSV file name
        csv_file = os.path.join(self.save_directory, "calibration_voltages.csv")

        # Generate header dynamically based on the number of inverters
        header = ['PSU Reference Voltage']
        header.extend([f'Inverter {i} Voltage(V)' for i in range(1, self.inverter_count + 1)])
        
        # Write the collected data to a CSV file
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_array)  # Write data

        print(f"Data written to {csv_file}")

    def currents_to_csv(self):
        #Convert list to numpy
        data_array = np.array(self.cdata_list)

        # Specify the CSV file name
        csv_file = os.path.join(self.save_directory, "calibration_currents.csv")

        # Generate header dynamically based on the number of inverters
        header = ['PSU Reference Current']
        header.extend([f'Inverter {i} Current(A)' for i in range(1, self.inverter_count + 1)])

        # Write the collected data to a CSV file
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_array)  # Write data

        print(f"Data written to {csv_file}")
    
    def get_vsize(self):
        num_rows = len(self.vdata_list)
        num_columns = len(self.vdata_list[0]) if self.vdata_list else 0  # Check if there are any rows      
        print(f"vNumber of rows: {num_rows}")
        print(f"vNumber of columns: {num_columns}")

    def get_csize(self):
        num_rows = len(self.cdata_list)
        num_columns = len(self.vdata_list[0]) if self.vdata_list else 0  # Check if there are any rows      
        print(f"cNumber of rows: {num_rows}")
        print(f"cNumber of columns: {num_columns}")
    
    def clear_data(self):
        self.vdata_list = []
        self.cdata_list = []
        self.get_vsize()
        self.get_csize()
