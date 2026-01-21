from dataclasses import dataclass

@dataclass
class Route:
    sequence: list
    number: int
    demand: float
    
    def __str__(self):
        return f"|{self.sequence}; {self.number}; {self.demand}|"