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
import os


power = "Machine1"
adc0 = MCP3008(device = 0)
interval = 0.15             # How long we want to wait between loops (in seconds)
sampleDelay = 0.20          # Waiting time between readings from channel (in seconds)
maxSamples = 5              # Maximum number of samples
channel = 4                 # Channel number from BCRobotics hat 
lineVoltage = 230           # Assumed voltage in the line
CTRange = 20                # Nominal Amps of the CT clamp 
deviceVoltage = 3.3         # Voltage of the device 3.3 for RPi or 5.0 for Arduino
phases = 1                  # The number of phases the device is connected to

while True:
	readValue = 0	
	for i in range(maxSamples):
		data = adc0.readData(channel)
		readValue = readValue + data
		time.sleep(sampleDelay)
	readValue = readValue / maxSamples 
	voltageVirtualValue = readValue * 0.707
	voltageVirtualValue = (voltageVirtualValue / 1024 * deviceVoltage) / 2
	ACCurrtntValue = voltageVirtualValue * CTRange
	powerValue = phases * ACCurrtntValue * lineVoltage 
	#print(ACCurrtntValue)
	var = "curl -i -XPOST 'http://172.18.0.2:8086/write?db=emon' --data '"+power+" current="+str(ACCurrtntValue)+",power="+str(powerValue)+"'"
	os.system(var)

