import traceback
import logging
import core.exceptions

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self,spec):
        self.spec = reversed(spec)
        self.contents = []

    def initialise(self,calculation_modules):
        for entry in self.spec:
            self.contents.append(calculation_modules[entry])

    def execute(self,sample_dict):
        variables_dict = {**sample_dict}
        for index,calc_module in enumerate(self.contents):
            try:
                output = calc_module.calculate(variables_dict)
                variables_dict = output
            except Exception as e:
                logger.error(f"Error during calculation: {traceback.format_exc()}")
                raise core.exceptions.CalculationError(str(e),self.spec[index])
        return variables_dict