from pathlib import Path
from copy import deepcopy
from typing import Type, Union, Any
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines.cache_utils import ignore_cache

class BaseBoardState(AbsBoardState):
    _DEFAULT_SAVE_MOD = None

    def __init__(self, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        self._board = None
        self._turn = 0
        self._curr_pid = 1

        self._save_mod = save_module

    def __eq__(self, other: 'BaseBoardState') -> bool:
        raise NotImplemented("The __eq__ method has not been implemented")

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def curr_pid(self) -> int:
        return self._curr_pid

    @property
    def board(self) -> Any:
        return self._board

    def play(self, move) -> 'AbsBoardState':
        raise NotImplemented("The play method has not been implemented")

    @ignore_cache
    def copy(self, *, cache=False) -> 'BaseBoardState':
        return deepcopy(self)

    def get_legal_moves(self, *, cache=False) -> set:
        raise NotImplemented("The get_legal_moves method has not been implemented")

    def winner(self) -> int:
        raise NotImplemented("The winner method has not been implemented")

    def score(self) -> tuple:
        raise NotImplemented("The score method has not been implemented")

    def save(self, file: Union[str, Path]):
        self._save_mod.save_state(file, self)

    @classmethod
    def load(cls, file: Union[str, Path], *, save_mod = None) -> 'BoardState':
        save_mod = save_mod if save_mod is not None else cls._DEFAULT_SAVE_MOD
        return save_mod.load_state(file, cls)
