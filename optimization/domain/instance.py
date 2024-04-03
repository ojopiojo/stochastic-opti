"""
This covers an instance of the optimization problem
"""
from datetime import datetime
from typing import List, Tuple

from optimization.domain.capability import Capability
from optimization.domain.machine import Machine
from optimization.domain.task import Task


class Instance:
    def __init__(
        self,
        tasks: list[Task],
        machines: list[Machine],
        capabilities: List[Capability],
        planning_horizon: Tuple[datetime, datetime],
    ):
        self.tasks = tasks
        self.machines = machines
        self.capabilities = capabilities
        self.planning_horizon = planning_horizon
