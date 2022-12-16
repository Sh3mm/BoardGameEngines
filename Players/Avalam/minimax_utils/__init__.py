from typing import Callable
from GameEngines.Avalam import BoardState

Heuristic = Callable[[BoardState, int], float]
DepthCalculator = Callable[[BoardState], float]
