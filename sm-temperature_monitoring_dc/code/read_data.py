# ----------------------------------------------------------------------
#
#    Temperature Monitoring (Basic solution) -- This digital solution enables, measures,
#    reports and records different  types of temperatures (ambient, process, equipment)
#    so that the temperature conditions surrounding a process can be understood and 
#    taken action upon. This version can work for 4 types of temperature sensors (now)
#    which include k-type, RTD, ambient (AHT20), and NIR-based sensors. 
#    The solution provides a Grafana dashboard that 
#    displays the temperature timeseries, set threshold value, and a state timeline showing the chnage in temperature.
#    An InfluxDB database is used to store timestamp, temperature, threshold and status. 
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
from smbus2 import SMBus
from mlx90614 import MLX90614
import os
from w1thermsensor import W1ThermSensor
import board
import digitalio
import logging
import tomli
import max6675
import adafruit_ahtx0




logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger("analysis.baseline");
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def get_config():
    with open("/app/config/config.toml", "rb") as f:
        toml_conf = tomli.load(f)
    logger.info(f"config:{toml_conf}")
    return toml_conf
    

class MLX90614_temp:
    def __init__(self):
        self.bus = SMBus(1)
        self.sensor=MLX90614(self.bus,address=0x5a)

    def ambient_temp(self):
        return self.sensor.get_amb_temp()

    def object_temp(self):
        return self.sensor.get_obj_temp()
        


class sht30:
    def __init__(self):
        self.bus = SMBus(1)
        self.bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        time.sleep(0.5)
        self.data = self.bus.read_i2c_block_data(0x44, 0x00, 6)

    def ambient_temp(self):
        self.temp = self.data[0] * 256 + self.data[1]
        return -45 + (175 * self.temp / 65535.0)



class W1Therm:
    def __init__(self):
        self.sensor = W1ThermSensor()
        

    def ambient_temp(self):
        return self.sensor.get_temperature()


class k_type:
    # https://github.com/archemius/MAX6675-Raspberry-pi-python/blob/master/temp_read_1_sensor.py
    def __init__(self):
        self.cs = 23
        self.sck = 24
        self.so = 25
        max6675.set_pin(self.cs, self.sck, self.so, 1) #[unit : 0 - raw, 1 - Celsius, 2 - Fahrenheit]
        

    def ambient_temp(self):
        return max6675.read_temp(self.cs)



class aht20:
    def __init__(self):
        i2c = board.I2C()
        self.sensor = adafruit_ahtx0.AHTx0(i2c)
        
    def ambient_temp(self):
        return self.sensor.temperature
        


def do_run(conf):
    
    machine_name = conf['machine'].get('name',"Machine Name Not Set")
    
    Threshold = conf['threshold']['t1']                # User sets the threshold in the config file
    
    if conf['sensing']['adc'] == 'MLX90614_temp':
        adc = MLX90614_temp()
    elif conf['sensing']['adc'] == 'W1ThermSensor':
        adc = W1Therm()
    elif conf['sensing']['adc'] == 'K-type':
        adc = k_type()
    elif conf['sensing']['adc'] == 'AHT20':
        adc = aht20()
    elif conf['sensing']['adc'] == 'SHT30':
        adc = sht30()
    else:
        raise Exception(f'ADC "{conf["sensing"]["adc"]}" not recognised/supported')
    
    
    #todo: error check on loaded in config
  
    while True:
        
        AmbientTemp = adc.ambient_temp()
        # ObjectTemp = adc.object_temp()
        if AmbientTemp > float(Threshold):
            AlertVal = 1
        else:
            AlertVal = 0

        logger.info(f"temperature_reading: {AmbientTemp}")
        var = "curl -i -XPOST 'http://172.18.0.2:8086/write?db=emon' --data '"+machine_name+" temp="+str(AmbientTemp)+",threshold="+str(Threshold)+",alertStatus="+str(AlertVal)+"'"
        os.system(var)
        time.sleep(1)


def run():
    conf = get_config()
    do_run(conf)

if __name__ == "__main__":
    run()
 