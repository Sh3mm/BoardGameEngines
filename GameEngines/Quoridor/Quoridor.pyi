from pathlib import Path
from typing import Set, Tuple, Dict, Any, Union
from numpy import ndarray
from GameEngines.abstract import AbsBoardState
from GameEngines.Quoridor.utilsTypes import Move

class BoardState(AbsBoardState):
    """
    This class is the implementation of BoardState for the `Quoridor` game.
    Rules for the game can be found online
    """

    def __init__(self): ...

    def __eq__(self, other: 'BoardState') -> bool: ...

    @property
    def curr_pid(self) -> int: ...

    @property
    def turn(self) -> int: ...

    @property
    def board(self) -> ndarray: ... # todo

    def __repr__(self) -> str: ...

    def copy(self, *, cache=False) -> 'BoardState': ...

    def play(self, move: Move,) -> 'BoardState': ...

    def get_legal_moves(self, *, cache=False) -> Set[Move]: ...

    def score(self) -> Tuple[int, int]: ...

    def winner(self) -> int: ...

    @staticmethod
    def load(file: Union[str, Path]) -> 'BoardState': ...

    def save(self, file: Union[str, Path]): ...