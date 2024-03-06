import traceback
import logging

logger = logging.getLogger(__name__)


class PiHat:
    ADCMax = pow(2, 12)

    def __init__(self, config, variables):
        self.channel = config.get('adc_channel')
        self.ADCVoltage = config.get('v_ref', 3.3)
        self.i2c = None

        self.input_variable = variables['v_in']

    def initialise(self, interface):
        self.i2c = interface

        try:
            check_device_bytes = self.i2c.read_register(0x00, 2,stop=True)
            check_device = check_device_bytes[1] << 8 + check_device_bytes[0]
            if check_device != 4:
                logger.warning(f"Grove Base Hat for RPi not detected on I2C bus")
                logger.debug(f"device_id reported: {check_device}")
        except Exception:
            logger.error(traceback.format_exc())

    def sample(self):
        try:
            # prepare register byte
            register_addr = 0x10 | (self.channel & 0x0F)
            # perform reading
            readings = self.i2c.read_register(register_addr, 2,stop=True)
            # calculate voltage
            adc_reading = (readings[1] << 8) + readings[0]
            voltage = (adc_reading / self.ADCMax) * self.ADCVoltage
            return {self.input_variable: voltage}
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e
