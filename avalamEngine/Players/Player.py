from abc import ABC, abstractmethod
from typing import Set, Callable
from avalamEngine import BoardState, Move
from avalamEngine.heuristics import Heuristic


class Player(ABC):

    def __int__(self, heuristic: Heuristic, p_name: str = None):
        self.name = p_name
        self.heuristic = heuristic

    @abstractmethod
    def play(self, board: BoardState, moves: Set[Move], pid: int, turn: int) -> Move:
        ...
