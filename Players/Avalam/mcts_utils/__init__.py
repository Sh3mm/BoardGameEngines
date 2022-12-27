from typing import Callable
from GameEngines.Avalam import BoardState

Simulator = Callable[[BoardState], float]

from Node import Node
from MctsTree import MctsTree
