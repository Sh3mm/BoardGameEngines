try:
    from .GameEngines import *

    __doc__ = GameEngines.__doc__
    if hasattr(GameEngines, "__all__"):
        __all__ = GameEngines.__all__

except ModuleNotFoundError:
    ...

from .abstract import AbsPlayer, AbsBoardState, AbsSaveModule
from .Game import Game
from .RandomPlayer import RandomPlayer
from .BaseBoardState import BaseBoardState

import GameEngines.UltiTTT
import GameEngines.Avalam
import GameEngines.Checkers
