from dataclasses import dataclass
from typing import List, Set

from optimization.domain.capability import Capability


@dataclass
class Machine:
    name: str
    capabilities: Set[Capability]
