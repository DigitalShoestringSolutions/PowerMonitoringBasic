from grove.adc import ADC as GroveADC


class ADC:
    def __init__(self, config):
        self.adc = GroveADC()
        self.channel = config['adc']['channel']
        self.ADCMax = pow(2, 10) - 1
        self.ADCVoltage = 3.3

    def sample(self):
        reading = self.adc.read_voltage(self.channel)
        voltage = (reading / self.ADCMax * self.ADCVoltage)
        return voltage
