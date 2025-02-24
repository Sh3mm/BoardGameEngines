from typing import List, Tuple, Set, Type
from GameEngines import BaseBoardState, AbsSaveModule
from GameEngines.UltiTTT import Move
from GameEngines.UltiTTT.repr import _repr
from GameEngines.UltiTTT.SaveModule import UltiTTTSave
from GameEngines.cache_utils import cache_moves
import numpy as np


class BoardState(BaseBoardState):

    _DEFAULT_SAVE_MOD = UltiTTTSave
    def __init__(self, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        super().__init__(save_module=save_module)

        self._board = np.zeros((9, 9), dtype=np.int8)
        self._win_state = [0] * 9 # The top level tic-tac-toe game
        self._active_cell = -1 # The active cell in the top level game

    def __deepcopy__(self, memodict={}):
        cp = BoardState.__new__(BoardState)
        BaseBoardState.__init__(cp, save_module=self._save_mod)
        cp._turn = self._turn
        cp._curr_pid = self._curr_pid

        cp._active_cell = self._active_cell

        cp._board = self._board.copy()
        cp._win_state = self._win_state.copy()
        return cp

    def __eq__(self, other: 'BoardState') -> bool:
        return (
            np.array_equal(self._board, other._board) and
            self._win_state == other._win_state and
            self._turn == other._turn and
            self._active_cell == other._active_cell and
            self._curr_pid == other._curr_pid
        )

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self):
        return _repr(self)

    def play(self, move: Move) -> 'BoardState':
        new_board = self.copy()
        new_board._turn += 1

        tile = 3 * move[0][0] + move[0][1]
        sub_tile = 3 * move[1][0] + move[1][1]

        new_board._board[tile, sub_tile] = self._curr_pid

        new_board._win_state[tile] = new_board._get_winner_of(new_board._board[tile])
        new_board._active_cell = sub_tile if new_board._win_state[sub_tile] == 0 else -1

        new_board._curr_pid = (self._curr_pid % 2) + 1

        return new_board

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        # if fist move or the active cell is full and any move can be taken
        if self._active_cell == -1:
            return {
                ((i // 3, i % 3), (j // 3, j % 3))
                for i, j in zip(*np.where(self._board == 0))
                if self._win_state[i] == 0
            }

        # if space left in the active cell
        return {
            ((self._active_cell // 3, self._active_cell % 3), (j // 3, j % 3))
            for j in np.where(self._board[self._active_cell] == 0)[0]
        }

    def winner(self) -> int:
        return self._get_winner_of(self._win_state)

    def score(self) -> Tuple[int, int]:
        w = self.winner()
        if w == 0 or w == -1:
            return 0, 0
        if w == 1:
            return 1, 0
        if w == 2:
            return 0, 1

    @staticmethod
    def _get_winner_of(section: List[int]) -> int:
        """function that take in a TTT board and return's the winner"""
         # winner
        diags = [section[0::4], section[2:8:2]]
        rows = [section[0 + (3 * i): 3 + (3 * i)] for i in range(3)]
        cols = [section[i::3] for i in range(3)]

        for line in diags + rows + cols:
            if (0 not in line) and (-1 not in line) and len(set(line)) == 1:
                return int(line[0])

        # tie
        if 0 not in section:
            return -1

        # not over
        return 0
