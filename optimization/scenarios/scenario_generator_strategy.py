from abc import ABC, abstractmethod


class ScenarioGeneratorStrategy(ABC):
    @staticmethod
    @abstractmethod
    def generate_scenarios(scenario_generator, instance):
        raise NotImplementedError
