import traceback
import logging
import random

logger = logging.getLogger(__name__)

class MockDeviceConstant:

    def __init__(self, config, variables):
        self.value = config.get('value')

        self.variable = variables['variable']

    def initialise(self, interface):
        pass

    def sample(self):
        try:
            return {self.variable: self.value}
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

class MockDeviceRandom:

    def __init__(self, config, variables):
        self.min = config.get('min',0)
        self.max = config.get('max')

        self.variable = variables['variable']

    def initialise(self, interface):
        pass

    def sample(self):
        try:
            return {self.variable: random.uniform(self.min, self.max)}
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e
