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

import logging
import math

logger = logging.getLogger("main.measure.conversion")


class PowerMonitoringCalculation:
    one_over_sqrt_2 = 1 / math.sqrt(2)

    def __init__(self, config):
        calculation_conf = config['calculation']
        self.AmplifierGain = calculation_conf['amplifier_gain']
        self.CTRange = calculation_conf['current_range']
        self.phases = calculation_conf['phases']
        self.lineVoltage = calculation_conf['voltage']

    def calculate(self, ADCAverageVoltage):
        AmplifierVoltageIn = ADCAverageVoltage / self.AmplifierGain
        CTClampCurrent = AmplifierVoltageIn * self.CTRange
        RMSCTClampCurrent = CTClampCurrent * self.one_over_sqrt_2

        PowerValue = self.phases * RMSCTClampCurrent * self.lineVoltage
        logger.debug(f"Vamp: {AmplifierVoltageIn} Irms: {RMSCTClampCurrent} P: {PowerValue}")
        return {"current": str(RMSCTClampCurrent), "power": str(PowerValue)}
