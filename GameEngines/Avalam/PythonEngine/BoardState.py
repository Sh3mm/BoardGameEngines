import numpy as np
from copy import deepcopy
from typing import Set
from itertools import product
from GameEngines._generic import AbsBoardState, cache_moves
from GameEngines.Avalam.repr import _repr
import GameEngines.Avalam.PythonEngine.utils as utils
from GameEngines.Avalam.utilsTypes import *


class BoardState(AbsBoardState):
    """
    This class is the Python implementation of BoardState for the `Avalam` game.
    Rules for the game can be found online
    """
    INIT_INFO = utils.board_setup()
    INIT_MOVES = utils.gen_moves(utils.board_setup()[0])

    def __init__(self):
        self._board, self._ratios = self.INIT_INFO
        self._moves = self.INIT_MOVES
        self._on_move_call = None
        self._turn = 0
        self._active_pid = 1

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def curr_pid(self) -> int:
        return self._active_pid

    @property
    def board(self) -> np.ndarray:
        return self._board

    @property
    def ratios(self) -> np.ndarray:
        return self._ratios

    def __repr__(self) -> str:
        return _repr(self)

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
        new_board._active_pid =  (self._active_pid % 2) + 1
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

    @classmethod
    def _load_data(cls, data):
        new_board = BoardState()
        new_board._board = data["board"]
        new_board._ratios = data["ratios"]
        new_board._moves = data["move_cache"]
        new_board._on_move_call = data["on_move_call"]
        new_board._turn = data["turn"]
        new_board._active_pid = data["active_pid"]

        return new_board

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
