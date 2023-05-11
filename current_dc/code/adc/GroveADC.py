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

from grove.adc import ADC as GroveADC
import logging

logger = logging.getLogger("main.measure.adc.grove")

class ADC:
    def __init__(self, config):
        if config['computing'] and config['computing']['hardware'] == "Rock4C+":
            self.adc = GroveADC(bus=7)
        else:
            self.adc = GroveADC()
        self.channel = config['adc']['channel']
        self.ADCMax = pow(2, 12) - 1
        self.ADCVoltage = 3.3

    def sample(self):
        voltage = self.adc.read_voltage(self.channel) / 1000
        logger.debug(f"v {voltage}")
        return voltage
