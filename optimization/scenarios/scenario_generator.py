from abc import ABC, abstractmethod

from optimization.domain.instance import Instance


class ScenarioGenerator(ABC):
    @abstractmethod
    def generate_by_index(self, instance: Instance):
        raise NotImplementedError

    @property
    @abstractmethod
    def index_range(self):
        raise NotImplementedError
