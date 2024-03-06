import time
import traceback
import logging

logger = logging.getLogger(__name__)


class ADS1115:
    # constants
    ADCMax = pow(2, 15)
    ADS111X_CONFIG_REGISTER = 0x01
    ADS111X_ADC_RESULT_REGISTER = 0x00
    ADS111X_GAINS = {
        '6.144V': (0b000, 6.144),
        '4.096V': (0b001, 4.096),
        '2.048V': (0b010, 2.048),
        '1.024V': (0b011, 1.024),
        '0.512V': (0b100, 0.512),
        '0.256V': (0b101, 0.256),
    }

    ADS111X_SAMPLE_SPEEDS = {
        '8SPS': (0b000, 1000 / 8),  # binary mask, sample delay in milliseconds
        '16SPS': (0b001, 1000 / 16),
        '32SPS': (0b010, 1000 / 32),
        '64SPS': (0b011, 1000 / 64),
        '128SPS': (0b100, 1000 / 128),
        '250SPS': (0b101, 1000 / 250),
        '475SPS': (0b110, 1000 / 475),
        '860SPS': (0b111, 1000 / 860),
    }

    def __init__(self, config, variables):
        self.channel = config.get('adc_channel')
        self.differential = config.get('differential', False)

        gain_string = config.get('gain', '4.096V')
        self.gain, self.ADCVoltage = self.ADS111X_GAINS.get(gain_string, (None, None))
        if self.gain is None:
            logger.warning("Invalid gain set in config, using default of 4.096V")
            self.gain, self.ADCVoltage = self.ADS111X_GAINS.get('4.096V')

        sps_string = config.get('speed', '128SPS')
        self.speed, self.sample_delay = self.ADS111X_SAMPLE_SPEEDS.get(sps_string, (None, None))
        if self.speed is None:
            logger.warning("Invalid speed set in config, using default of 128SPS")
            self.speed, self.sample_delay = self.ADS111X_SAMPLE_SPEEDS.get('128SPS')

        self.i2c = None

        self.input_variable = variables['v_in']

    def initialise(self, interface):
        self.i2c = interface

    def sample(self):
        try:
            # prepare config byte
            config = self.make_config_bytes()
            # trigger sample
            sample_time = time.monotonic_ns()
            buffer_out = self.i2c.write_register(self.ADS111X_CONFIG_REGISTER, config)
            # delay while sample taken
            time.sleep(self.sample_delay / 1000)

            # ensure sleep was long enough
            while time.monotonic_ns() - sample_time < self.sample_delay * 1000 * 1000:
                time.sleep((time.monotonic_ns() - sample_time) / (1000 * 1000 * 1000))

            buffer_out = self.i2c.read_register(self.ADS111X_ADC_RESULT_REGISTER, 2)
            # calculate voltage
            adc_reading = (buffer_out[0] << 8) + buffer_out[1]
            if adc_reading > 32767:
                adc_reading -= 65535
            voltage = (adc_reading / self.ADCMax) * self.ADCVoltage
            return {self.input_variable: voltage}
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def make_config_bytes(self):
        msb = 0x00
        msb |= 1 << 7  # start single shot conversion
        if not self.differential:
            msb |= 0b1 << 6
        msb |= (self.channel & 0b11) << 4
        msb |= self.gain << 1
        msb |= 0b1  # single shot mode

        lsb = 0x00
        lsb |= self.speed << 5
        lsb |= 0b00011  # no comparator
        return [msb, lsb]
