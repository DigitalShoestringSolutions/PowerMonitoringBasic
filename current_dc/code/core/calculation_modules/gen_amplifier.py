import traceback
import logging

logger = logging.getLogger(__name__)


class GenAmplifier:
    def __init__(self, config,variables):
        self.gain = config.get('gain')
        self.amp_input = variables.get('amp_input')
        self.amp_output = variables.get('amp_output', self.amp_input)

    def calculate(self, var_dict):
        try:
            # Get variable containing output value
            value = var_dict[self.amp_output]
            if value is not None:
                # Divide by gain to get input value
                value = value / self.gain
                # Set the input variable
                var_dict[self.amp_input] = value
            else:
                logger.warning(f"GenAmplifier: amplifier output variable '{self.amp_output}' not found")
        except Exception:
            logger.error(traceback.format_exc())
        return var_dict
