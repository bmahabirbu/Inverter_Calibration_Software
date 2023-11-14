# Code for N76 Power supply
print("Welcome to the Server Side Inverter Calibration Firmware (seperated files)!\n")

import kpsu_controller as KPSU
import data_manager as DM
import particle_manager as PM
import sys

# Initalize classes
kpsu = KPSU.kn67psu_controller()
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
            ref_voltage = kpsu.control_power_supply(voltage_setpoint=volt_inc, current_setpoint=kpsu.stable_curr)
            measured_voltages = pm.get_measured_voltages()
            measured_voltages.insert(0, ref_voltage)
            dm.append_voltages(measured_voltages)
            volt_inc += kpsu.increment_v
        except Exception as e: 
            print(f"An unexpected voltage sweep error occurred:")
            raise e
    dm.voltages_to_csv()
    # turn off psu
    kpsu.control_power_supply(voltage_setpoint=0, current_setpoint=0)

def full_current_sweep():
    kpsu.set_vc_flag('current')
    curr_inc = kpsu.start_c_value
    while curr_inc <= kpsu.max_current:
        try:
            ref_current = kpsu.control_power_supply(voltage_setpoint=kpsu.stable_volt, current_setpoint=curr_inc)
            measured_currents = pm.get_measured_currents()
            measured_currents.insert(0, ref_current)
            dm.append_currents(measured_currents)
            curr_inc += kpsu.increment_c
        except Exception as e:  
            print(f"An unexpected current sweep error occurred:")
            raise e
    dm.currents_to_csv()
    # turn off psu
    kpsu.control_power_supply(voltage_setpoint=0, current_setpoint=0)
        
        
def get_calibration():
    try:
        full_voltage_sweep()
        full_current_sweep()
        print("Calibration complete")
    except ConnectionError:  # Catch the connection error
        return
    except Exception as e:  
        return  