import spidev

pip_requirements = {"spidev":"3.6"}

class SPI:
    def __init__(self,config):
        self.bus = config.get('bus', 0)
        self.device = config.get('device', 0)
        self.default_speed = config.get('speed', 1000000)
        self.default_mode = config.get('mode', 0)
        self.spi = spidev.SpiDev()

    def initialise(self):
        self.spi.open(self.bus, self.device)

    def transfer(self, bytes,mode = None,speed = None):
        self.spi.mode = self.default_mode if mode is None else mode
        self.spi.max_speed_hz  = self.default_speed if speed is None else speed
        return self.spi.xfer2(bytes)
