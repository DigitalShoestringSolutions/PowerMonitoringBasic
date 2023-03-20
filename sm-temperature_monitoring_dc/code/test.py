# sudo pip3 install w1thermsensor
#  https://bigl.es/ds18b20-temperature-sensor-with-python-raspberry-pi/


# import time
# import board
# import digitalio
# import adafruit_max31855
# import adafruit_dht
# import RPi.GPIO as gpio


# spi = board.SPI()
# cs = digitalio.DigitalInOut(board.D4)
# so = digitalio.DigitalInOut(board.D25)
# sck = digitalio.DigitalInOut(board.D24)
# sensor = adafruit_max31855.MAX31855(spi, cs)


# # sensor = adafruit_dht.DHT11(23)
        


# while True:
#     temperature = sensor.temperature
#     print("The temperature is %s celsius" % temperature)
#     time.sleep(1)

# import max6675
# import time

# cs = 23
# sck = 24
# so = 25

# max6675.set_pin(cs, sck, so, 1)


# import time

# import adafruit_dht
# import board

# dht = adafruit_dht.DHT22(board.D17)

# while True:
#     try:
#         temperature = dht.temperature
#         humidity = dht.humidity
#         # Print what we got to the REPL
#         print("Temp: {:.1f} *C \t Humidity: {}%".format(temperature, humidity))
#     except RuntimeError as e:
#         # Reading doesn't always work! Just print error and we'll try again
#         print("Reading from DHT failure: ", e.args)

#     time.sleep(1)

import time
import board
import adafruit_ahtx0

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    print("Humidity: %0.1f %%" % sensor.relative_humidity)
    time.sleep(2)