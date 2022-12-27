import GameEngines
from GameEngines.Avalam import *

__doc__ = GameEngines.Avalam.__doc__
if hasattr(GameEngines.Avalam, "__all__"):
    __all__ = GameEngines.Avalam.__all__

from .utilsTypes import Move, Coords
from .BoardState import BoardState
