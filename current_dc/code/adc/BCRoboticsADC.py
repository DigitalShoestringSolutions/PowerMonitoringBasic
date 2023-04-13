from bcr_mcp3008 import MCP3008


class ADC:
    def __init__(self, config):
        self.adc = MCP3008(device=0)
        self.channel = config['adc']['channel']
        self.ADCMax = pow(2, 10) - 1
        self.ADCVoltage = 3.3

    def sample(self):
        reading = self.adc.readData(self.channel)
        voltage = (reading / self.ADCMax * self.ADCVoltage)
        return voltage
