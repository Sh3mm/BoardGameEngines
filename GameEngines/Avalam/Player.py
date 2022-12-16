from abc import ABC, abstractmethod
from typing import Set
from GameEngines.Avalam import BoardState, Move


class Player(ABC):
    @abstractmethod
    def play(self, board: BoardState, moves: Set[Move], pid: int, turn: int) -> Move:
        ...

    def get_name(self) -> str:
        return 'Unnamed'
