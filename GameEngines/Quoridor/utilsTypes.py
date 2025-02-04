from typing import Any, Tuple, Union
from dataclasses import dataclass
from enum import IntEnum

class MoveType(IntEnum):
    WALL = 0,
    JUMP = 1

class WallType(IntEnum):
    V = 0, # Vertical
    H = 1  # Horizontal


Coords = Tuple[int, int]
Jump = Tuple[Coords, Coords]
Wall = Tuple[WallType, Coords]
Move = Tuple[MoveType, Union[Wall, Jump]]

@dataclass(frozen=True)
class PlayerInfo:
    pos: int
    walls: int

def to_move(move: Any) -> Move:
    pass # todo
