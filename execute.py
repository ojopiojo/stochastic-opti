from datetime import datetime

import pandas as pd
from ortools.linear_solver import pywraplp

from optimization.domain.capability import Capability
from optimization.domain.instance import Instance
from optimization.domain.machine import Machine
from optimization.domain.task import Task
from optimization.model.base_model import BaseModel
from optimization.model.changed_task_duration_submodel import (
    ChangedTaskDurationSubModelExpander,
)
from optimization.scenarios.exhaustive_strategy import (
    ExhaustiveScenarioGeneratorStrategy,
)
from optimization.scenarios.no_strategy import NoGeneratorStrategy
from optimization.scenarios.task_delay_scenario_generator import (
    TaskDelayScenarioGenerator,
)
from optimization.solver.base_model_parameters import BaseModelParametersBuilder
from uuid import uuid4

from optimization.solver.stochastic_solver import StochasticSolver

task_id = "basic"
start_date = datetime(year=2024, month=1, day=1)
end_date = datetime(year=2024, month=2, day=15)
planning_horizon = (start_date, end_date)

tasks_df = pd.read_csv(f"input/{task_id}_tasks.csv")
machines_df = pd.read_csv(f"input/{task_id}_machines.csv")

capabilities = {}
capability_names = set()
for capability in machines_df["capabilities"]:
    for capability_name in capability.split(","):
        capability_names.add(capability_name)

for capability_name in capability_names:
    capabilities[capability_name] = Capability(name=capability_name, id=uuid4())


def parse_capabilities(capabilities_set):
    return {capabilities[name] for name in capabilities_set.split(",")}


task_list = []
for i, task in tasks_df.iterrows():
    task_list.append(
        Task(
            name=task["name"],
            delay_probability=task["delay_probability"],
            base_duration=task["base_duration"],
            delayed_duration=task["delayed_duration"],
            target_date=datetime.strptime(task["target_date"], "%Y-%m-%d"),
            early_penalty=task["early_penalty"],
            late_penalty=task["late_penalty"],
            required_capabilities=parse_capabilities(task["required_capabilities"]),
        )
    )

machine_list = []
for i, machine in machines_df.iterrows():
    machine_list.append(
        Machine(
            name=machine["name"],
            capabilities=parse_capabilities(machine["capabilities"]),
        )
    )

print(f"Number of tasks: {len(task_list)}")
print(f"Number of machines: {len(machine_list)}")
instance = Instance(
    tasks=task_list,
    machines=machine_list,
    capabilities=list(capabilities.values()),
    planning_horizon=planning_horizon,
)

solver = StochasticSolver(
    TaskDelayScenarioGenerator(task_list),
    NoGeneratorStrategy(),
    BaseModelParametersBuilder(),
    ChangedTaskDurationSubModelExpander(),
)

solver.solve(instance)
