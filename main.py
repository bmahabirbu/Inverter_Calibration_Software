# Code for N76 Power supply
print("Welcome to the Server Side Inverter Calibration Firmware (seperated files)!\n")

import kpsu_controller as KPSU
from kpsu_controller import time
import data_manager as DM
import particle_manager as PM
import sys

# Initalize classes
kpsu = KPSU.kn57psu_controller()
pm = PM.particle_manager()

# # Get Inverter count than initalize data manager
# inverter_num = int(pm.get_inverter_num())
# print("Number of Inverters = "+str(inverter_num))
# # If no inverters connect abort
# if inverter_num <= 0:
#     sys.exit()

dm = DM.data_manager(3)


def full_voltage_sweep():
    kpsu.set_vc_flag('volts')
    volt_inc = kpsu.start_v_value
    while volt_inc <= kpsu.max_voltage:
        try:
            kpsu.control_power_supply(voltage_setpoint=volt_inc, current_setpoint=kpsu.stable_curr)
            measured_voltages = pm.get_measured_voltages()
            measured_voltages.insert(0, volt_inc)
            dm.append_voltages(measured_voltages)
            volt_inc += kpsu.increment_v
        except Exception as e: 
            print(f"An unexpected voltage sweep error occurred:")
            raise e
    dm.voltages_to_csv()
    # turn off psu
    kpsu.control_power_supply(voltage_setpoint=0, current_setpoint=0)
    time.sleep(10)
    print("Finished Voltage Measurements")

def voltage_sign_wave():
    direction = 1
    kpsu.set_vc_flag('volts')
    volt_inc = kpsu.start_v_value
    while True:
        try:
            kpsu.control_power_supply(voltage_setpoint=volt_inc, current_setpoint=kpsu.max_current)
            volt_inc += kpsu.increment_v * direction
            # Code for sign wave
            if volt_inc >= kpsu.max_voltage:
                volt_inc = kpsu.max_voltage
                direction = -1  # Change direction to decrement
            elif volt_inc <= kpsu.start_v_value:
                volt_inc = kpsu.start_v_value
                direction = 1  # Change direction to increment
    
        except Exception as e: 
            print(f"An unexpected voltage signwave error occurred:")
            raise e
    # turn off psu
    kpsu.control_power_supply(voltage_setpoint=0, current_setpoint=0)
    time.sleep(10)
    print("Finished Voltage sign wave")

def full_current_sweep():
    kpsu.set_vc_flag('current')
    curr_inc = kpsu.start_c_value
    while curr_inc <= kpsu.max_current:
        try:
            # New current setting method see kpsu attributes for more details
            V = kpsu.c_factor * curr_inc
            rounded_V = round(V, 3)
            kpsu.control_power_supply(voltage_setpoint=rounded_V, current_setpoint=kpsu.max_current)
            measured_currents = pm.get_measured_currents()
            measured_currents.insert(0, curr_inc)
            dm.append_currents(measured_currents)
            curr_inc += kpsu.increment_c
        except Exception as e:  
            print(f"An unexpected current sweep error occurred:")
            raise e
    dm.currents_to_csv()
    # turn off psu
    kpsu.control_power_supply(voltage_setpoint=0, current_setpoint=0)
    time.sleep(10)
    print("Finished Current Measurements")
        
        
def get_calibration():
    try:
        full_voltage_sweep()
        full_current_sweep()
        print("Calibration complete")
    except ConnectionError:  # Catch the connection error
        return
    except Exception as e:  
        return

voltage_sign_wave()