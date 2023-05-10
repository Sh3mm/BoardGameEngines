from typing import Set
import numpy as np

from GameEngines._generic import AbsBoardState
from GameEngines.Checkers.repr import _repr
from GameEngines.Checkers.utilsTypes import *


class BoardState(AbsBoardState):
    """
    This class is the Python implementation of BoardState for the `Checkers` game.
    Rules for the game can be found online
    """

    def __init__(self):
        pass

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self) -> str:
        return _repr(self)

    def copy(self) -> 'BoardState':
        pass

    def play(self, move: Move, pid: int = None) -> 'BoardState':
        pass

    def get_legal_moves(self, pid=0) -> Set[Move]:
        pass

    def score(self) -> Tuple[int, int]:
        pass

    def winner(self) -> int:
        pass
