import math
import traceback
import logging

logger = logging.getLogger(__name__)

class RMSToPeak:
    one_over_sqrt_2 = 1 / math.sqrt(2)

    def __init__(self, config,variables):
        self.var_in = variables.get('var_in')
        self.var_out = variables.get('var_out')

    def calculate(self, var_dict):
        try:
            # Get variable containing output value
            value = var_dict[self.var_out]
            if value is not None:
                # Divide by sqrt 2 to get RMS
                value = value * self.one_over_sqrt_2
                # Set the input variable
                var_dict[self.var_in] = value
            else:
                logger.warning(f"RMSToPeak: output variable '{self.var_out}' not found")
        except Exception:
            logger.error(traceback.format_exc())
        return var_dict

class PowerToCurrent:
    one_over_sqrt_3 = 1 / math.sqrt(3)
    def __init__(self, config,variables):
        self.line_voltage = config.get('line_voltage')
        self.phase_voltage = config.get('phase_voltage')
        self.phases = config.get('phases',1)

        if self.phase_voltage is None:
            if self.phase_voltage:
                self.phase_voltage = self.line_voltage * self.one_over_sqrt_3
            else:
                self.phase_voltage = 230
                logger.warning("Phase voltage not specified - using default of 230V")

        self.power_in = variables.get('power_in')
        self.rms_current_out = variables.get('rms_current_out')

    def calculate(self, var_dict):
        try:
            # Get variable containing output value
            rms_line_current = var_dict[self.rms_current_out]
            if rms_line_current is not None:
                # 3 Phase:
                # Power = sqrt(3) * V_line * I_line
                # V_line = sqrt(3) * V_phase
                # > Power = 3 * V_phase * I_line
                # Single phase:
                # Power = (1) * V_phase * I_line
                #
                # >> (Apparent) Power = n_phases * V_phase * I_line

                power = self.phases * rms_line_current * self.phase_voltage
                # Set the input variable
                var_dict[self.power_in] = power
            else:
                logger.warning(f"PowerToCurrent: output current variable '{self.rms_current_out}' not found")
        except Exception:
            logger.error(traceback.format_exc())
        return var_dict

class PowerToVoltageCurrent:
    one_over_sqrt_3 = 1 / math.sqrt(3)
    def __init__(self, config,variables):
        self.phases = config.get('phases',1)

        self.power_in = variables.get('power_in')
        self.rms_current_out = variables.get('rms_current_out')
        self.rms_phase_voltage_out = variables.get('rms_phase_voltage_out')

    def calculate(self, var_dict):
        try:
            # Get variable containing output value
            rms_line_current = var_dict[self.rms_current_out]
            rms_phase_voltage = var_dict[self.rms_phase_voltage_out]

            if rms_line_current is not None:
                if rms_phase_voltage is not None:
                    # 3 Phase:
                    # Power = sqrt(3) * V_line * I_line
                    # V_line = sqrt(3) * V_phase
                    # > Power = 3 * V_phase * I_line
                    # Single phase:
                    # Power = (1) * V_phase * I_line
                    #
                    # >> (Apparent) Power = n_phases * V_phase * I_line

                    power = self.phases * rms_line_current * rms_phase_voltage
                    # Set the input variable
                    var_dict[self.power_in] = power
                else:
                    logger.warning(f"PowerToVoltageCurrent: output voltage variable '{self.rms_phase_voltage_out}' not found")
            else:
                logger.warning(f"PowerToVoltageCurrent: output current variable '{self.rms_current_out}' not found")
        except Exception:
            logger.error(traceback.format_exc())
        return var_dict