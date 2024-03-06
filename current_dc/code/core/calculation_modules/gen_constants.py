import traceback
import logging

logger = logging.getLogger(__name__)

class DefaultConstant:
    def __init__(self, config,variables):
        self.value = config.get('value')
        self.variable = variables.get('variable')

    def calculate(self, var_dict):
        try:
            var_dict.setdefault(self.variable, self.value)
        except:
            pass
        return var_dict

class RenameDefaultConstant:
    def __init__(self, config,variables):
        self.value = config.get('value')
        self.original = variables.get('original_variable')
        self.new = variables.get('new_variable')

    def calculate(self, var_dict):
        try:
            if self.original in var_dict:
                var_dict[self.new] = self.value
        except:
            pass
        return var_dict

class FixedConstant:
    def __init__(self, config,variables):
        self.value = config.get('value')
        self.variable = variables.get('variable')

    def calculate(self, var_dict):
        try:
            var_dict[self.variable] = self.value
        except:
            pass
        return var_dict