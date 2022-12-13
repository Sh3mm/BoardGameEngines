from Avalam.PythonEngine import BoardState
from typing import Callable, Union

Heuristic = Callable[[BoardState, int], float]
DepthCalculator = Callable[[BoardState], Union[float, int]]
