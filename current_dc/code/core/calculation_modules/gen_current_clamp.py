import traceback
import logging

logger = logging.getLogger(__name__)


class VoltageClamp:
    def __init__(self, config,variables):
        self.nominal_voltage = config.get('nominal_voltage', 1)  # e.g. 1 = 1V
        self.nominal_current = config.get('nominal_current')  # e.g. 20 = 20A

        self.output_voltage_variable = variables.get('voltage_out')
        self.input_current_variable = variables.get('current_in', 'current')

    def calculate(self, var_dict):
        try:
            # Get clamp output voltage
            v_clamp = var_dict[self.output_voltage_variable]
            if v_clamp is not None:
                # Multiply clamp output voltage by nominal ratio to get input current
                current = (v_clamp / self.nominal_voltage) * self.nominal_current
                # Set the input current variable
                var_dict[self.input_current_variable] = current
            else:
                logger.warning(f"VoltageClamp: output voltage variable '{self.output_voltage_variable}' not found")
        except Exception:
            logger.error(traceback.format_exc())

        return var_dict
