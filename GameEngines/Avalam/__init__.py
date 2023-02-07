import GameEngines
from GameEngines.Avalam import *
from .utilsTypes import Move, Coords

try:
    __doc__ = GameEngines.Avalam.__doc__
    if hasattr(GameEngines.Avalam, "__all__"):
        __all__ = GameEngines.Avalam.__all__

    from .BoardState import BoardState

except AttributeError:
    from .PythonEngine.BoardState import BoardState
