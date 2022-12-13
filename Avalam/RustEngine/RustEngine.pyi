from typing import Set, Tuple
from numpy import ndarray

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]

def gen_moves(board: ndarray) -> Set[Move]: ...

class BoardState(object):
    board: ndarray
    ratios: ndarray
    moves: Set[Move]

    def __init__(self): ...

    def __repr__(self) -> str: ...

    def copy(self) -> BoardState: ...

    def stack(self, origin: Coords, dest: Coords) -> BoardState: ...

    def get_legal_moves(self) -> Set[Move]: ...

    def count(self) -> Tuple[int, int]: ...