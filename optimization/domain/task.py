"""

"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Set

from optimization.domain.capability import Capability


@dataclass
class Task:
    name: str
    delay_probability: float
    base_duration: int
    delayed_duration: int
    target_date: datetime
    early_penalty: float
    late_penalty: float
    required_capabilities: Set[Capability]
