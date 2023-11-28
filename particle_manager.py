import requests
from requests.exceptions import Timeout
'''
Particle manager class
Functionality:
1) Contains code that interfaces with the particle controller to get voltage and current measurements
2) Interfaces with the particle controller to switch inverter boards and gain info on total amount and which one is currently being measured
2) This class also utilizes import delay mechanism 
'''
class particle_manager:

    def __init__(self):
        self.url = "https://api.particle.io/v1/devices"
        self.device_id = ""
        self.access_token = ""

        self.volt_call = "getVoltages"
        self.curr_call = "getCurrents"
        self.inverter_num_call = "getInverterCount"

        #5 seconds for connection 5 seconds for response
        self.timeout = (5, 20)
    
    def get_measured_voltages(self):
        print("Getting Voltages from Inverters")
        full_url = f"{ self.url}/{self.device_id}/{self.volt_call}?access_token={self.access_token}"

        try:
            # Make the GET request with the specified timeout
            response = requests.get(full_url, timeout=self.timeout)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                result_str = response.json()["result"]
                result_list = result_str.split(", ")
                print("Connection Successful Result: "+str(result_list))
                return result_list
            else:
                print("Error:", response.status_code, response.text)

        except Timeout:
            print("Request timed out.")
        except Exception as e:
            print("An error occurred:", e)

    def get_measured_currents(self):
        print("Getting Currents from Inverters")
        full_url = f"{ self.url}/{self.device_id}/{self.curr_call}?access_token={self.access_token}"

        try:
            # Make the GET request with the specified timeout
            response = requests.get(full_url, timeout=self.timeout)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                result_str = response.json()["result"]
                result_list = result_str.split(", ")
                print("Connection Successful Result: "+str(result_list))
                return result_list
            else:
                print("Error:", response.status_code, response.text)

        except Timeout:
            print("Request timed out.")
        except Exception as e:
            print("An error occurred:", e)

    def get_inverter_num(self):
        print("Getting number of Inverters")
        full_url = f"{ self.url}/{self.device_id}/{self.inverter_num_call}?access_token={self.access_token}"
        try:
            # Make the GET request with the specified timeout
            response = requests.get(full_url, timeout=self.timeout)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                result_str = response.json()["result"]
                result_list = result_str.split(", ")
                print("Connection Successful")
                return result_list[0]
            else:
                print("Error:", response.status_code, response.text)

        except Timeout:
            print("Request timed out.")
        except Exception as e:
            print("An error occurred:", e)

    # TODO!

    # def get_inverter_names(self):
    #     # nice to have
    #     pass
