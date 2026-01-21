from dataclasses import dataclass

@dataclass
class FlowEdge:
    to: int
    capacity: float
    cost: float
    rev: int
