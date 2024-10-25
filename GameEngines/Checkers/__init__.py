import GameEngines
from GameEngines.Checkers import *
from .utilsTypes import Move, Coords

try:
    __doc__ = GameEngines.Checkers.__doc__
    if hasattr(GameEngines.Checkers, "__all__"):
        __all__ = GameEngines.Checkers.__all__

    from .BoardState import BoardState

except AttributeError:
    from .PythonEngine.BoardState import BoardState
