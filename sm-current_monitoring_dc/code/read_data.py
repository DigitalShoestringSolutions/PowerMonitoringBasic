# ----------------------------------------------------------------------
#
#    Power Monitoring (Basic solution) -- This digital solution measures,
#    reports and records both AC power and current consumed by an electrical 
#    equipment, so that its energy consumption can be understood and 
#    taken action upon. This version comes with one current transformer 
#    clamp of 20A that is buckled up to the electric line the equipment 
#    is connected to. The solution provides a Grafana dashboard that 
#    displays current and power consumption, and an InfluxDB database 
#    to store timestamp, current and power. 
#
#    Copyright (C) 2022  Shoestring and University of Cambridge
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.
#
# ----------------------------------------------------------------------

import time
from bcr_mcp3008 import MCP3008
from grove.adc import ADC
from DFRobot_ADS1115 import ADS1115
import os

import logging
import tomli

logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger("analysis.baseline");
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def get_config():
    with open("/app/config/config.toml", "rb") as f:
        toml_conf = tomli.load(f)
    logger.info(f"config:{toml_conf}")
    return toml_conf
    
class BCRoboticsADC:
    def __init__(self):
        self.adc = MCP3008(device = 0)
        
    def sample(self,channel):
        return self.adc.readData(channel)
        
class GroveADC:
    def __init__(self):
        self.adc = ADC()
        
    def sample(self,channel):
        return self.adc.read_voltage(channel)
        
class GravityADC:
    def __init__(self):
        self.adc = ADS1115()
        
    def sample(self,channel):
        self.adc.set_addr_ADS1115(0x48) # See the physical switch on the module and change accordingly
        return self.adc.read_voltage(channel)['r']

def do_run(conf):
    
    interval = 0.15             # How long we want to wait between loops (in seconds)
    sampleDelay = 0.20          # Waiting time between readings from channel (in seconds)
    maxSamples = 5              # Maximum number of samples
    lineVoltage = 230           # Assumed voltage in the line
    
    deviceVoltage = 3.3         # Voltage of the device 3.3 for RPi or 5.0 for Arduino
    phases = 1                  # The number of phases the device is connected to
    
    machine_name = conf['machine'].get('name',"Machine Name Not Set")
    
    CTRange = conf['sensing']['current_range']                # Nominal Amps of the CT clamp 
    
    if conf['sensing']['adc'] == 'BCRobotics':
        adc = BCRoboticsADC()
    elif conf['sensing']['adc'] == 'Grove':
        adc = GroveADC()
    elif conf['sensing']['adc'] == 'Gravity':
        adc = GravityADC()
    else:
        raise Exception(f'ADC "{conf["sensing"]["adc"]}" not recognised/supported')
    
    channel = conf['sensing']['channel']          # Channel number from BCRobotics hat 
    
    #todo: error check on loaded in config
  
    while True:
        readValue = 0	
        for i in range(maxSamples):
            data = adc.sample(channel)
            readValue = readValue + data
            time.sleep(sampleDelay)
        readValue = readValue / maxSamples 
        voltageVirtualValue = readValue * 0.707
        voltageVirtualValue = (voltageVirtualValue / 1024 * deviceVoltage) / 2
        ACCurrtntValue = voltageVirtualValue * CTRange
        powerValue = phases * ACCurrtntValue * lineVoltage 
        logger.info(f"current_reading: {ACCurrtntValue}")
        var = "curl -i -XPOST 'http://172.18.0.2:8086/write?db=emon' --data '"+machine_name+" current="+str(ACCurrtntValue)+",power="+str(powerValue)+"'"
        os.system(var)


def run():
    conf = get_config()
    do_run(conf)

if __name__ == "__main__":
    run()
