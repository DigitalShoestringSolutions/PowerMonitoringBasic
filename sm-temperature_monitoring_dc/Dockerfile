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

FROM python:3

ADD ./code/ /app

#RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir rpi.gpio 
RUN pip3 install bcr-libraries
RUN pip3 install spidev
# RUN pip3 install Pillow
RUN pip3 install tomli
RUN git clone https://github.com/Seeed-Studio/grove.py /grove && cd /grove && pip3 install . && rm -r /grove
#RUN pip3 install time
#RUN apt-get update && apt-get install -yq python3-smbus
# RUN pip3 install --upgrade adafruit-python-shell
# RUN wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py && python3 raspi-blinka.py
# RUN pip3 install adafruit-blinka
RUN pip3 install smbus2
RUN pip3 install PyMLX90614
RUN pip3 install w1thermsensor
RUN pip3 install board
RUN pip3 install adafruit-circuitpython-ahtx0
# RUN pip3 install Adafruit-Blinka
# RUN pip3 install adafruit-circuitpython-max31855
CMD [ "python3", "/app/read_data.py"]
