from typing import Set, Tuple
from numpy import ndarray
from GameEngines.Avalam.utilsTypes import Move, Coords

class RawAvalamState(object):
    board: ndarray
    ratios: ndarray
    moves: Set[Move]

    def __init__(self): ...

    def __repr__(self) -> str: ...

    def copy(self) -> RawAvalamState: ...

    def play(self, origin: Coords, dest: Coords) -> RawAvalamState: ...

    def get_legal_moves(self) -> Set[Move]: ...

    def count(self) -> Tuple[int, int]: ...