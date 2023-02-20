import GameEngines
from GameEngines.UltiTTT import *

from .utilsTypes import Move, Coords

try:
    __doc__ = GameEngines.UltiTTT.__doc__
    if hasattr(GameEngines.UltiTTT, "__all__"):
        __all__ = GameEngines.UltiTTT.__all__

    from .BoardState import BoardState

except AttributeError:
    from .PythonEngine.BoardState import BoardState
