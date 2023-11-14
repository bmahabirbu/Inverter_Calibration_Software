# Import other libraries
import time

# Import library that interfaces with the keysight power supply 
import pyvisa

'''
kn67psu_controller class
Functionality:
1) Contains code necessary to interface with a keysight n76 power supply
2) Contains code to set voltage and current over LAN
3) TO DO: Create a subclass that controls en e36300 power supply
'''

class kn67psu_controller:
    # config values
    ip_address = "10.10.223.99"
    max_retry_attempts = 3
    set_vc_delay = 1

    # Start inc and limit Values for while loop 
    start_v_value = 0.0
    increment_v = 1.0
    max_voltage= 50.0

    start_c_value = 0.0
    increment_c = 0.5
    max_current = 10.0

    #Stable current value for voltage sweep
    stable_curr = 0.2
    #Stable voltage value for current sweep
    stable_volt = 50.0

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
        try:
            self.connect_to_power_supply()
        except pyvisa.errors.VisaIOError as e:
            print("Power supply is disconnected. Aborting...")
            return
        
        # Initialize the voltage inc value
        volt_inc = self.start_v_value
        # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                while volt_inc <= self.max_voltage:
                    self.set_voltage(volt_inc)
                    self.set_current(self.stable_curr)
                    self.enable_output()

                    self.read_voltage()
                    self.read_current()
                    # Continue
                    volt_inc += self.increment_v
                    time.sleep(self.set_vc_delay)
                    retry_successful = True
            except Exception as e:
                retry_count += 1
                print(f"An error occurred in voltage sweep test: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                    time.sleep(self.set_vc_delay)
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Close the connection
            self.close_resource()
        except NameError:
            pass  # The variable was not defined
    
    def current_sweep_check(self):
        try:
            self.connect_to_power_supply()
        except pyvisa.errors.VisaIOError as e:
            print("Power supply is disconnected. Aborting...")
            return
        
        # Initialize the current inc value
        curr_inc = self.start_c_value
         # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                while curr_inc <= self.max_current:
                    self.set_voltage(curr_inc)
                    self.set_current(self.stable_volt)
                    self.enable_output()
                    self.read_voltage()
                    self.read_current()

                    # Continue
                    curr_inc += self.increment_c
                    time.sleep(self.set_vc_delay)
                    retry_successful = True
            except Exception as e:
                retry_count += 1
                print(f"An error occurred in voltage sweep test: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                    time.sleep(self.set_vc_delay)
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Close the connection
            self.close_resource()
        except NameError:
            pass  # The variable was not defined

    def control_power_supply(self, voltage_setpoint, current_setpoint):
        try:
            self.connect_to_power_supply()
        except pyvisa.errors.VisaIOError as e:
            raise e
        
        # Set the maximum number of retry attempts
        retry_count = 0
        retry_successful = False

        while retry_count < self.max_retry_attempts and retry_successful == False:
            try:
                self.set_voltage(voltage_setpoint)
                self.set_current(current_setpoint)
                self.enable_output()

                voltage_actual = self.read_voltage()
                current_actual = self.read_current()

                # Probably want to add some rounding if were using the actual measurements
                if self.vc_flag == 'volts':
                    output = voltage_actual
                elif self.vc_flag == 'current':
                    output = current_actual
                else:
                    print("error getting flag")
        
                time.sleep(self.set_vc_delay)
                retry_successful = True

            except Exception as e:
                retry_count += 1
                print(f"An error occurred setting voltage and current: {e}")
                if retry_count < self.max_retry_attempts:
                    print(f"Retrying ({retry_count}/{self.max_retry_attempts})...")
                    time.sleep(self.set_vc_delay)
                else:
                    print("Max retry attempts reached. Exiting.")
        try:
            # Close the connection
            self.close_resource()
            return output
        except NameError:
            pass  # The variable was not defined