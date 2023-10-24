# ----------------------------------------------------------------------
#
#    MCP3008 library -- This file is part of the Power Monitoring (Basic
#    solution) distribution. It contains all the commands needed to
#    assemble an image of the solution on a ROCK (Pi) 4C Plus with Ubuntu
#    Server version 20.04 LTS (focal) 64 bits.
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

import spidev

class MCP3008:    

    def __init__(self, device = 0):
            self.device = device
            self.spi = spidev.SpiDev()
            self.create()
            self.spi.max_speed_hz = 1000000 

    #create the MCP3008 Devices (0 or 1) on Bus 0
    def create(self):
        self.spi.open(1, self.device)
        self.spi.max_speed_hz = 1000000
        
    #read Data from the specific channel (0-7)
    def readData(self, channel = 0):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    #close the device
    def close(self):
        self.spi.close()
