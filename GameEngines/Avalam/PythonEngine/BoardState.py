from typing import Set, Type, Optional
import numpy as np

from GameEngines import BaseBoardState, AbsSaveModule
from GameEngines.cache_utils import cache_moves

from GameEngines.Avalam.repr import _repr
from GameEngines.Avalam.SaveModule import AvalamSave
import GameEngines.Avalam.PythonEngine.utils as utils
from GameEngines.Avalam.utilsTypes import *


class BoardState(BaseBoardState):
    """
    This class is the Python implementation of BoardState for the `Avalam` game.
    Rules for the game can be found online
    """
    INIT_INFO = utils.board_setup()
    _DEFAULT_SAVE_MOD = AvalamSave

    def __init__(self, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        super().__init__(save_module=save_module)

        self._board: np.ndarray = self.INIT_INFO[0]
        self._ratios: np.ndarray = self.INIT_INFO[1] # Table of the ratios of each piece type in towers
        self._moves: Set[Move] = set() # Deprecated. Kept for parity with the Rust engine
        self._on_move_call: Optional[Move] = None # Deprecated. Kept for parity with the Rust engine

    def __eq__(self, other: 'BoardState') -> bool:
        return (
            np.array_equal(self._board, other._board) and
            np.array_equal(self._ratios, other._ratios) and
            self._turn == other._turn and
            self._curr_pid == other._curr_pid
        )

    @property
    def board(self) -> np.ndarray:
        return self._board

    @property
    def ratios(self) -> np.ndarray:
        return self._ratios

    def __repr__(self) -> str:
        return _repr(self)

    def play(self, move: Move) -> 'BoardState':
        origin: Coords = move[0]
        dest: Coords = move[1]

        new_board = self.copy()
        new_board._turn += 1

        top = new_board._board[origin]
        new_board._board[origin] = 0
        bottom = new_board._board[dest]
        new_board._board[dest] = np.sign(top) * abs(bottom) + top

        new_board._update_ratios(origin, dest)

        new_board._curr_pid = (self._curr_pid % 2) + 1
        return new_board

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        abs_board: np.ndarray[int] = np.abs(self._board)
        towers = ((0 < abs_board) & (abs_board < 5))

        def f(i, j):
            base = np.zeros((3, 3))
            base[
            max(0, i-1) - i+1: min(9, i+2) - i+1,
            max(0, j-1) - j+1: min(9, j+2) - j+1
            ] = abs_board[max(0, i-1):i+2, max(0, j-1):j+2]
            return base.flatten()

        non_zero = towers.nonzero()
        coords = list(zip(*non_zero))

        to = np.fromiter((f(i, j) for i, j in coords), np.dtype((np.int64, (9,))))
        to[:, 4] = 0

        value = np.repeat(abs_board[non_zero][:, np.newaxis], 9, axis=1)

        possibilities = value + to
        positions = zip(*((value < possibilities) & (possibilities <= 5)).nonzero())

        return set(
            (coords[i], (coords[i][0] - 1 + (j // 3), coords[i][1] - 1 + (j % 3)))
            for i, j in positions
        )

    def score(self) -> Tuple[int, int]:
        return (
            (self._board > 0).sum(),
            (self._board < 0).sum()
        )

    def winner(self) -> int:
        if self._has_moves():
            return 0

        p1, p2 = self.score()
        # tie
        if p1 == p2:
            return -1
        # winner
        return int(p1 < p2) + 1

    def _update_ratios(self, origin: Coords, dest: Coords):
        """method used to update the ratios for the state upon creation"""
        self._ratios[:, dest[0], dest[1]] += self._ratios[:, origin[0], origin[1]]
        self._ratios[:, origin[0], origin[1]] = 0

    def _has_moves(self) -> bool:
        abs_board: np.ndarray[int] = np.abs(self._board)
        towers = ((0 < abs_board) & (abs_board < 5))

        for i, j in zip(*towers.nonzero()):
            to = np.zeros((3, 3))
            to[
            max(0, i-1) - i+1: min(9, i+2) - i+1,
            max(0, j-1) - j+1: min(9, j+2) - j+1
            ] = abs_board[max(0, i-1):i+2, max(0, j-1):j+2]
            to = to.flatten()
            to[4] = 0

            value = abs_board[(i, j)]

            possibilities = to + value
            if np.sum((value < possibilities) & (possibilities <= 5)) > 1:
                return True

        return False