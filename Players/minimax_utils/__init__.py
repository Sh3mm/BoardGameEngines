from typing import Callable
from Avalam import BoardState

Heuristic = Callable[[BoardState, int], float]
DepthCalculator = Callable[[BoardState], float]
