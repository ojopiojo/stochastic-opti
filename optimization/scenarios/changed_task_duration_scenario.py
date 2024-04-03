from optimization.scenarios.scenario import Scenario


class ChangedTaskDurationScenario(Scenario):
    def __init__(self, name, weight, task_duration: dict[int, int]):
        self.name = name
        self.weight = weight
        self.task_duration = task_duration
