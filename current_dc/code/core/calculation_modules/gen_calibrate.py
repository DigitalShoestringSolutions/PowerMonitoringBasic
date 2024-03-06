import traceback
import logging

logger = logging.getLogger(__name__)


class MultiplierOffset:
    def __init__(self, config,variables):
        self.multiplier = config.get('multiplier',1)
        self.offset = config.get('offset',0)

        self.raw_value = variables.get('raw_value')
        self.calibrated_value = variables.get('calibrated_value', self.raw_value)

    def calculate(self, var_dict):
        try:
            # Get variable containing output value
            value = var_dict[self.raw_value]
            if value is not None:
                # Divide by gain to get input value
                out = value * self.multiplier + self.offset
                # Set the input variable
                var_dict[self.calibrated_value] = out
            else:
                logger.warning(f"MultiplierOffset: raw variable '{self.raw_value}' not found")
        except Exception:
            logger.error(traceback.format_exc())
        return var_dict
