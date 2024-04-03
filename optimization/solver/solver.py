from abc import ABC, abstractmethod

from optimization.domain.instance import Instance


class Solver(ABC):
    @abstractmethod
    def solve(self, instance: Instance):
        raise NotImplementedError
