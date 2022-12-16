from typing import Set, Tuple
from numpy import ndarray

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]

class RawBoardState(object):
    board: ndarray
    ratios: ndarray
    moves: Set[Move]

    def __init__(self): ...

    def __repr__(self) -> str: ...

    def copy(self) -> RawBoardState: ...

    def play(self, origin: Coords, dest: Coords) -> RawBoardState: ...

    def get_legal_moves(self) -> Set[Move]: ...

    def count(self) -> Tuple[int, int]: ...