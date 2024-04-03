"""
Creates a domain and constraints to be consumed by the model
"""
from abc import ABC, abstractmethod
from optimization.domain.instance import Instance


class ModelParameters(ABC):
    pass


class ModelParametersBuilder(ABC):
    @abstractmethod
    def build(self, instance: Instance):
        pass
