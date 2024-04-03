from abc import ABC, abstractmethod

from optimization.model.base_model import BaseModel
from optimization.scenarios.scenario import Scenario


class SubModel(ABC):
    name: str
