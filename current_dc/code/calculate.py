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
