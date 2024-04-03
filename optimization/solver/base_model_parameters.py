from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

from optimization.domain.capability import Capability
from optimization.domain.instance import Instance
from optimization.domain.machine import Machine
from optimization.domain.task import Task
from optimization.solver.model_parameters import ModelParametersBuilder


@dataclass
class BaseModelParameters:
    M: list[int]
    S: list[int]
    y: set[tuple[int, int]]
    j: set[tuple[int, int]]
    delay_costs: dict[int, float]
    advance_costs: dict[int, float]
    target_execution_times: dict[int, int]
    task_duration: dict[int, int]
    start_date: int
    end_date: int


class BaseModelParametersBuilder(ModelParametersBuilder):
    tasks: List[Task]
    machines: List[Machine]
    capabilities: List[Capability]
    planning_horizon: Tuple[datetime, datetime]
    start_date = 0
    end_date = 0

    M = []
    S = []
    y = set()
    j = set()
    S_delay = {}
    S_advance = {}
    delay_costs = {}
    advance_costs = {}
    target_execution_times = {}
    task_duration = {}

    def __init__(
        self,
    ):
        pass

    def build(self, instance: Instance):
        self.instance = instance
        self.tasks = instance.tasks
        self.machines = instance.machines
        self.capabilities = instance.capabilities
        self.planning_horizon = instance.planning_horizon
        self.start_date = 0
        self.end_date = (self.planning_horizon[1] - self.planning_horizon[0]).days

        self.build_basic_arrays()
        self.build_constants()
        self.build_domain()

        return BaseModelParameters(
            self.M,
            self.S,
            self.y,
            self.j,
            self.delay_costs,
            self.advance_costs,
            self.target_execution_times,
            self.task_duration,
            self.start_date,
            self.end_date,
        )

    def build_basic_arrays(self):
        self.M = [i for i in range(len(self.machines))]
        self.S = [i for i in range(len(self.tasks))]

    def build_domain(self):
        self.y = self.build_machine_assignment_variables()
        self.j = self.build_task_order_variables()

    def build_constants(self):
        self.delay_costs = self.build_delay_costs()
        self.advance_costs = self.build_advance_costs()
        self.target_execution_times = self.build_target_execution_times()
        self.task_duration = self.build_task_duration()

    @staticmethod
    def __can_machine_perform_task(machine, task):
        return task.required_capabilities.issubset(machine.capabilities)

    def build_machine_assignment_variables(self):
        y = set()
        for m in self.M:
            for s in self.S:
                if self.tasks[s].required_capabilities.issubset(
                    self.machines[m].capabilities
                ):
                    y.add((m, s))
        return y

    def build_task_order_variables(self):
        j = set()
        for r in self.S:
            for s in self.S:
                if r != s:
                    j.add((r, s))
        return j

    def build_delay_costs(self):
        return {s: self.tasks[s].late_penalty for s in self.S}

    def build_advance_costs(self):
        return {s: self.tasks[s].early_penalty for s in self.S}

    def __date_to_day(self, date):
        return (date - self.planning_horizon[0]).days

    def build_target_execution_times(self) -> dict[int, int]:
        return {s: self.__date_to_day(self.tasks[s].target_date) for s in self.S}

    def build_task_duration(self):
        return {s: self.tasks[s].base_duration for s in self.S}
