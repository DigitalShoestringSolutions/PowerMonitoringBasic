from abc import ABC, abstractmethod

class CalculationInterface(ABC):
    @abstractmethod
    def __init__(self, config: dict) -> None:
        pass

    @abstractmethod
    def calculate(self, input_dict: dict) -> dict:
        pass



class DeviceInterface(ABC):
    @abstractmethod
    def __init__(self, config: dict) -> None:
        pass

    @abstractmethod
    def initialise(self) -> None:
        pass

    @abstractmethod
    def sample(self) -> dict:
        pass

