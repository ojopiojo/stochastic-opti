from abc import ABC, abstractmethod


class Scenario(ABC):
    name: str
    weight: float
