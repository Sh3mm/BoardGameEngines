from typing import Set, Tuple, Dict, Any, Type
from numpy import ndarray
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines.Avalam.utilsTypes import Move
from GameEngines.Avalam.SaveModule import AvalamSave

class BoardState(AbsBoardState):
    """
    This class is the implementation of BoardState for the `Avalam` game.
    Rules for the game can be found online
    """
    _DEFAULT_SAVE_MOD = AvalamSave

    def __init__(self, *, save: Type['AbsSaveModule'] = _DEFAULT_SAVE_MOD): ...

    @property
    def curr_pid(self) -> int: ...

    @property
    def turn(self) -> int: ...

    @property
    def board(self) -> ndarray: ...

    @property
    def ratios(self) -> ndarray: ...

    def __repr__(self) -> str: ...

    def copy(self, *, cache=False) -> 'BoardState': ...

    def play(self, move: Move) -> 'AbsBoardState': ...

    def get_legal_moves(self, *, cache=False) -> Set[Move]: ...

    def score(self) -> Tuple[int, int]: ...

    def winner(self) -> int: ...

    @classmethod
    def _load_data(cls, data: Dict[str, Any]) -> 'AbsBoardState': ...
