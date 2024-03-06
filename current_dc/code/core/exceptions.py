
class SampleError(Exception):
    def __init__(self, message,device):
        super().__init__(message)
        self.device = device

class CalculationError(Exception):
    def __init__(self, message,module):
        super().__init__(message)
        self.module = module