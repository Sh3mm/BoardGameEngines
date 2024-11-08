from pathlib import Path

import numpy as np
from copy import deepcopy
from typing import Set, Type, Optional, Union
from itertools import product
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines.cache_utils import cache_moves, ignore_cache

from GameEngines.Avalam.repr import _repr
from GameEngines.Avalam.SaveModule import AvalamSave
import GameEngines.Avalam.PythonEngine.utils as utils
from GameEngines.Avalam.utilsTypes import *


class BoardState(AbsBoardState):
    """
    This class is the Python implementation of BoardState for the `Avalam` game.
    Rules for the game can be found online
    """
    INIT_INFO = utils.board_setup()
    INIT_MOVES = utils.gen_moves(utils.board_setup()[0])
    _DEFAULT_SAVE_MOD = AvalamSave

    def __init__(self, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        self._board: np.ndarray = self.INIT_INFO[0]
        self._ratios: np.ndarray = self.INIT_INFO[1]
        self._moves: Set[Move] = self.INIT_MOVES
        self._on_move_call: Optional[Move] = None
        self._turn: int = 0
        self._curr_pid: int = 1

        self._save_mod: AbsSaveModule = save_module()

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def curr_pid(self) -> int:
        return self._curr_pid

    @property
    def board(self) -> np.ndarray:
        return self._board

    @property
    def ratios(self) -> np.ndarray:
        return self._ratios

    def __repr__(self) -> str:
        return _repr(self)

    @ignore_cache
    def copy(self) -> 'BoardState':
        return deepcopy(self)

    def play(self, move: Move) -> 'AbsBoardState':
        origin: Coords = move[0]
        dest: Coords = move[1]

        new_board = self.copy()
        new_board._turn += 1

        top = new_board._board[origin]
        new_board._board[origin] = 0
        bottom = new_board._board[dest]
        new_board._board[dest] = (int(top > 0) * 2 - 1) * abs(bottom) + top

        new_board._update_ratios(origin, dest)

        new_board._on_move_call = (origin, dest)
        new_board._curr_pid = (self._curr_pid % 2) + 1
        return new_board

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        if self._on_move_call is not None:
            self._update_moves(*self._on_move_call)
            self._on_move_call = None
        return self._moves

    def score(self) -> Tuple[int, int]:
        return (
            (self._board > 0).sum(),
            (self._board < 0).sum()
        )

    def winner(self) -> int:
        # unfinished
        if len(self.get_legal_moves()) > 0:
            return 0

        p1, p2 = self.score()
        # tie
        if p1 == p1:
            return -1
        # winner
        return int(p1 < p2) + 1


    def save(self, file: Union[str, Path]):
        self._save_mod.save_state(file, self)

    @classmethod
    def load(cls, file: Union[str, Path], *, save_mod = _DEFAULT_SAVE_MOD) -> 'BoardState':
        return cls._DEFAULT_SAVE_MOD.load_state(file, BoardState)

    def _update_moves(self, origin: Coords, dest: Coords):
        """method used to update the cached moves for the state upon creation"""
        for i, j in product(range(-1, 2), range(-1, 2)):
            self._moves.discard((origin, (origin[0] + i, origin[1] + j)))
            self._moves.discard(((origin[0] + i, origin[1] + j), origin))

        for i, j in product(range(-1, 2), range(-1, 2)):
            if not (0 <= dest[0] + i < 9 and
                    0 <= dest[1] + j < 9):
                continue
            if abs(self._board[dest]) + abs(self._board[(dest[0] + i, dest[1] + j)]) > 5:
                self._moves.discard(((dest[0] + i, dest[1] + j), dest))
                self._moves.discard((dest, (dest[0] + i, dest[1] + j)))

    def _update_ratios(self, origin: Coords, dest: Coords):
        """method used to update the ratios for the state upon creation"""
        self._ratios[:, dest[0], dest[1]] += self._ratios[:, origin[0], origin[1]]
        self._ratios[:, origin[0], origin[1]] = 0
