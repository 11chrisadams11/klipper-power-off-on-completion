#!/usr/bin/python3 -u
# pylint: disable=C0326,C0301
'''
Script to take info from Klipper and power off printer when print is complete
'''
import sys
import time
import json
import math
import requests

## Modify these settings to your liking ##

POWER_OFF_WHEN_COMPLETE = True
BED_TEMP_FOR_POWER_OFF = 50
HOTEND_TEMP_FOR_POWER_OFF = 40

MOONRAKER_HOST = 'localhost'
MOONRAKER_PORT = 7125

## End settings ##


class MoonrakerAPI:
    ''' Create Moonraker API class '''
    def __init__(self, host, port):
        self.moonraker_host = host
        self.moonraker_port = str(port)
        self.moonraker_url = f"http://{self.moonraker_host}:{self.moonraker_port}"
        self.bed_base_temp = False
        self.extruder_base_temp = False

    def printer_state(self):
            ''' Get printer status '''
            url = f"{self.moonraker_url}/printer/objects/query?print_stats"
            try:
                ret = requests.get(url)
            except requests.exceptions.ConnectionError:
                return False
            try:
                return ret.json()['result']['status']['print_stats']['state']
            except KeyError:
                return False

    def printing_stats(self):
        ''' Get stats for bed heater, hotend, and printing percent '''
        url = f"{self.moonraker_url}/printer/objects/query?heater_bed&extruder&display_status"
        data = requests.get(url).json()

        bed_temp = data['result']['status']['heater_bed']['temperature']
        bed_target = data['result']['status']['heater_bed']['target']
        ## Set base temperatures to make heating progress start from the bottom of strip
        if not self.bed_base_temp:
            self.bed_base_temp = bed_temp if bed_temp else 0

        extruder_temp = data['result']['status']['extruder']['temperature']
        extruder_target = data['result']['status']['extruder']['target']
        ## Set base temperatures to make heating progress start from the bottom of strip
        if not self.extruder_base_temp:
            self.extruder_base_temp = extruder_temp if extruder_temp else 0

        return {
            'bed': {
                'temp': float(bed_temp),
                'heating_percent': heating_percent(bed_temp, bed_target, self.bed_base_temp),
                'power_percent': round(data['result']['status']['heater_bed']['power'] * 100)
            },
            'extruder': {
                'temp': float(extruder_temp),
                'heating_percent': heating_percent(extruder_temp, extruder_target, self.extruder_base_temp),
                'power_percent': round(data['result']['status']['extruder']['power'] * 100)
            },
            'printing': {
                'done_percent': round(data['result']['status']['display_status']['progress'] * 100)
            }
        }

    def power_status(self):
        ''' Get printer power status '''
        url = f"{self.moonraker_url}/machine/device_power/devices?device=printer"
        try:
            ret = requests.get(url)
            return ret.json()['result']['devices'][0]['status']
        except (KeyError, requests.exceptions.ConnectionError) as err:
            print(f'Error getting power state.\n{err}')
            return 'off'

    def power_off(self):
        ''' Power off the printer '''
        url = f"{self.moonraker_url}/machine/device_power/off?printer"
        try:
            return requests.post(url).json()
        except (KeyError, requests.exceptions.ConnectionError) as err:
            print(f'Error powering off printer.\n{err}')
            return False


def heating_percent(temp, target, base_temp):
    ''' Get heating percent for given component '''
    if target == 0.0:
        return 0
    return math.floor(((temp - base_temp) * 100) / (target - base_temp))


def run():
    ''' Do work son '''
    moonraker_api_cl = MoonrakerAPI(MOONRAKER_HOST, MOONRAKER_PORT)

    power_off_counter = 0
    try:
        while True:
            printer_state_ = moonraker_api_cl.printer_state()
            # print(printer_state_)
            if printer_state_ == 'complete':
                if moonraker_api_cl.power_status() == 'on':
                    power_off_counter += 1
                    if POWER_OFF_WHEN_COMPLETE and power_off_counter > 9:
                        power_off_counter = 0
                        printing_stats = moonraker_api_cl.printing_stats()
                        bed_temp = printing_stats['bed']['temp']
                        extruder_temp = printing_stats['extruder']['temp']
                        # print(f'\nBed temp: {round(bed_temp, 2)}\nExtruder temp: {round(extruder_temp, 2)}\n')
                        if (bed_temp < BED_TEMP_FOR_POWER_OFF and extruder_temp < HOTEND_TEMP_FOR_POWER_OFF):
                            print('Powering off printer')
                            moonraker_api_cl.power_off()

            time.sleep(5)
    
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    run()
