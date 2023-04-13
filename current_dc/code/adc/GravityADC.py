from adc.DFRobot_ADS1115 import ADS1115


class ADC:
    def __init__(self, config):
        self.adc = ADS1115()
        self.channel = config['adc']['channel']
        self.ADCMax = 1024
        self.ADCVoltage = 1.024
        self.I2CAddress = config['adc'].get('i2c_address', 0x48)

    def sample(self):
        self.adc.set_addr_ADS1115(self.I2CAddress)  # See the physical switch on the module and change accordingly
        reading = self.adc.read_voltage(self.channel)['r']
        voltage = (reading / self.ADCMax * self.ADCVoltage)
        return voltage
