import GameEngines
from GameEngines.Quoridor import *

from .utilsTypes import Move, MoveType, Jump, Wall, WallType, Coords, PlayerInfo

try:
    __doc__ = GameEngines.Quoridor.__doc__
    if hasattr(GameEngines.Quoridor, "__all__"):
        __all__ = GameEngines.Quoridor.__all__

    from .BoardState import BoardState

except AttributeError:
    from .PythonEngine.BoardState import BoardState