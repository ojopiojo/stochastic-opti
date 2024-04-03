from typing import List

from optimization.domain.task import Task
from optimization.scenarios.changed_task_duration_scenario import (
    ChangedTaskDurationScenario,
)
from optimization.scenarios.scenario_generator import ScenarioGenerator


class TaskDelayScenarioGenerator(ScenarioGenerator):
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks

    @property
    def index_range(self):
        return [0, 2 ** len(self.tasks)]

    def index_iterator(self):
        return range(*self.index_range)

    def generate_by_index(self, index):
        i = 0
        delayed_tasks = set()
        while (1 << i) <= index:
            if index & (1 << i) > 0:
                delayed_tasks.add(i)

            i += 1

        task_duration = {}
        weight = 1
        for s, task in enumerate(self.tasks):
            if s in delayed_tasks:
                task_duration[s] = task.delayed_duration
                weight *= task.delay_probability
            else:
                task_duration[s] = task.base_duration
                weight *= 1 - task.delay_probability

        return ChangedTaskDurationScenario(
            name=f"Task delay scenario {index}",
            weight=weight,
            task_duration=task_duration
        )
