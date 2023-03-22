# ----------------------------------------------------------------------
#
#    Dockerfile script -- This file is part of the Power Monitoring (Basic 
#    solution) distribution. It contains all the commands needed to 
#    assemble an image of the solution on a Raspberry Pi 4b with raspbian 
#    OS version 11 (bullseye) 32 bits. 
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
RUN pip3 install Pillow
RUN pip3 install tomli
RUN git clone https://github.com/Seeed-Studio/grove.py /grove && cd /grove && pip3 install . && rm -r /grove
#RUN pip3 install time
#RUN apt-get update && apt-get install -yq python3-smbus
RUN pip3 install smbus2
#CMD ["bash", "setup-i2c.sh"]
# CMD modprobe i2c-dev && python /app/demo.py 
CMD [ "python3", "/app/read_data.py"]
