from typing import Set, Tuple
from numpy import ndarray
from GameEngines._generic import AbsBoardState
from GameEngines.Checkers.utilsTypes import Move

class BoardState(AbsBoardState):
    """
    This class is the implementation of BoardState for the `Avalam` game.
    Rules for the game can be found online
    """
    ratios: ndarray

    def __init__(self): ...

    @property
    def turn(self) -> int: ...

    @property
    def board(self) -> ndarray: ...

    def __repr__(self) -> str: ...

    def copy(self) -> 'BoardState': ...

    def play(self, move: Move) -> 'AbsBoardState': ...

    def get_legal_moves(self, *, cache=False) -> Set[Move]: ...

    def score(self) -> Tuple[int, int]: ...

    def winner(self) -> int: ...