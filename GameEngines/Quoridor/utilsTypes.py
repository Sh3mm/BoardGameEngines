from typing import Any, Tuple, Union
from typing import NamedTuple
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

class PlayerInfo(NamedTuple):
    pos: int
    walls: int

def to_move(move: Any) -> Move:
    if move[0] is MoveType.WALL:
        return MoveType.WALL, (WallType(move[1][0]), move[1][1])
    elif move[0] is MoveType.JUMP:
        return MoveType.JUMP, (move[1][0], move[1][1])
    else:
        raise ValueError(f"{move} is cannot be converted to Move")