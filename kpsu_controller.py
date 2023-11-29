# Import other libraries
import time

# Import library that interfaces with the keysight power supply 
import pyvisa

'''
kn57psu_controller class
Functionality:
1) Contains code necessary to interface with a keysight N5767A Power Supply, 60 V, 25 A, 1500 W
2) Contains code to set voltage and current over LAN
3) TO DO: Create a class that controls the e36300 power supply
'''

class kn57psu_controller:
    # config values
    ip_address = "10.10.223.99"
    max_retry_attempts = 3
    v_delay = 1
    # 30 Seconds to Wait for Resistor to Dissipate Heat
    c_delay = 60
    # Start inc and limit values for voltage sweep
    start_v_value = 0.0
    increment_v = 1.0
    max_voltage= 50.0

    # Conversion Factor for Current Measurement
    # Circuit is connected in parallel with the inverter 
    # having a 4 ohm resistor and 2 25 ohm shunt resistors 
    # To reduce the psu spike current when switching to current mode

    # Below is the math

    # R1 = 4 ohms
    # R2 = 50 ohms
    # R equivalent = [1/R1 + 1/R2]^-1
    # R eq = 100/27
    # V = IR
    # V = 100/27*I
    c_factor = 100.0/27.0

    # Instead of having a high voltage and changing current values
    # The new method is to set the current at max output and calculate
    # what the max current will be from setting a specific voltage

    # For example, at 10V the max current would be 2.7 amps
    # I = 27/100 * 10 = 27/10 = 2.7
    # So the sweep would change the voltage to match a current 
    # loop of 0-10 amps. i.e solve for voltage. 27/100 * V = I
    # So now we have a formula that can map what voltage is needed to get the desired amps
    start_c_value = 0.0
    increment_c = 0.5
    max_current = 10.0

    #Stable current value for voltage sweep
    stable_curr = 0.2

    def __init__(self):
        #default value
        self.vc_flag = 'volts'
    
    def connect_to_power_supply(self):
        # Actual Voltage and current return from keysight powersupply measurement
        # Replace 'TCPIP0::192.168.1.100::inst0::INSTR' with your instrument's VISA resource address
        visa_resource = f"TCPIP::{self.ip_address}::INSTR"

        # Initialize the VISA resource manager
        rm = pyvisa.ResourceManager()

        # Open connection to power supply, do nothing if already opened
        try:
            self.ps = rm.open_resource(visa_resource)
            # The resource was successfully opened  
        except pyvisa.errors.VisaIOError as e:
            if "resource is already open" in str(e):
                print("Power supply connection already opened")
            else:
                print(f"Cant connect to psu error located in kpsu.connct_to_power_supply()!: {e}")
                raise e
    
    def close_resource(self):
        self.ps.close()

    def enable_output(self):
        response = self.ps.query('OUTP?')  # Query the output state
        if response.strip() == '1':  # Check if the response indicates that the output is already enabled
            print("Power supply output is already enabled")
        else:
            self.ps.write('OUTP ON')
            print("Power supply output turned on")

    def disable_output(self):
        response = self.ps.query('OUTP?')  # Query the output state
        if response.strip() == '0':  # Check if the response indicates that the output is already disabled
            print("Power supply output is already disabled")
        else:
            self.ps.write('OUTP OFF')
            print("Power supply output turned off")

    def get_id(self):
        # Query the instrument's identification
        identification = self.ps.query('*IDN?')
        print(f"Instrument Identification: {identification}")
        
    def set_vc_flag(self, string):
        if string == 'volts':
            self.vc_flag = string
        elif string == 'current':
            self.vc_flag = string
        else:
            print("Invalid string to change vc_flag")
    
    def set_voltage(self, voltage_setpoint):
        self.ps.write(f'VOLT {voltage_setpoint}')
        print(f"Set Voltage: {voltage_setpoint} V")

    def set_current(self, current_setpoint):
        self.ps.write(f'CURR {current_setpoint}')
        print(f"Set Current: {current_setpoint} A")
        
        
    def read_voltage(self):
        voltage_actual = self.ps.query('MEAS:VOLT?')
        print(f"Actual Voltage: {voltage_actual} V")
        return voltage_actual

    def read_current(self):
        current_actual = self.ps.query('MEAS:CURR?')
        print(f"Actual Current: {current_actual} A")
        return current_actual
    
    def voltage_sweep_check(self):
        # Initialize the voltage inc value
        volt_inc = self.start_v_value
        # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                self.connect_to_power_supply()
                self.enable_output()
                while volt_inc <= self.max_voltage:
                    self.set_voltage(volt_inc)
                    self.set_current(self.stable_curr)
                    
                    self.read_voltage()
                    self.read_current()
                    # Continue
                    volt_inc += self.increment_v
                    time.sleep(self.v_delay)
                    retry_successful = True
            except Exception as e:
                retry_count += 1
                print(f"An error occurred in voltage sweep test: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Set voltage and current low and turn off output
            self.set_voltage(0)
            self.set_current(0)
            self.disable_output()
            # Close the connection
            self.close_resource()
        except NameError:
            pass  # The variable was not defined
    
    def current_sweep_check(self):
        # Initialize the current inc value
        curr_inc = self.start_c_value
         # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                self.connect_to_power_supply()
                self.enable_output()
                while curr_inc <= self.max_current:
                    # New method for setting current 
                    V = self.c_factor * curr_inc
                    rounded_V = round(V, 3)

                    self.set_voltage(rounded_V)
                    self.set_current(self.max_current)
                    
                    self.read_voltage()
                    self.read_current()

                    # Continue
                    curr_inc += self.increment_c
                    print("Wait for Resistor to Dissipate Heat Seconds: "+str(self.c_delay))
                    time.sleep(self.c_delay)
                    print("Continuing")
                    retry_successful = True
            except Exception as e:
                retry_count += 1
                print(f"An error occurred in voltage sweep test: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Set voltage and current low and turn off output
            self.set_voltage(0)
            self.set_current(0)
            self.disable_output()
            # Close the connection
            self.close_resource()
        except NameError:
            pass  # The variable was not defined

    def control_power_supply(self, voltage_setpoint, current_setpoint):
        # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                self.connect_to_power_supply()
                self.set_voltage(voltage_setpoint)
                self.set_current(current_setpoint)
                self.enable_output()

                # Reads the output of the keysight psu
                voltage_actual = self.read_voltage()
                current_actual = self.read_current()

                # Probably want to add some rounding if were using the actual measurements
                if self.vc_flag == 'volts':
                    output = voltage_actual
                    time.sleep(self.v_delay)
                    retry_successful = True
                elif self.vc_flag == 'current':
                    output = current_actual
                    print("Wait for Resistor to Dissipate Heat Seconds: "+str(self.c_delay))
                    time.sleep(self.c_delay)
                    print("Continuing")
                    retry_successful = True
                else:
                    print("error getting flag")

            except Exception as e:
                retry_count += 1
                print(f"An error occurred setting voltage and current: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Close the connection
            self.close_resource()
            return output
        except NameError:
            pass  # The variable was not defined