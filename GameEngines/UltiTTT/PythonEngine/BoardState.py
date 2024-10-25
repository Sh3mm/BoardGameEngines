from typing import List, Tuple
from GameEngines.UltiTTT import Move
from GameEngines.UltiTTT.repr import _repr
from GameEngines import AbsBoardState
import numpy as np


class BoardState(AbsBoardState):
    def __init__(self, board: np.ndarray = None, win_state: List[int] = None, active_cell=None, turn=None):
        if board is None or win_state is None or active_cell is None or turn is None:
            turn = 0
            board = np.zeros((9, 9), dtype=np.int8)
            win_state = [0] * 9
            active_cell = -1

        self._turn = turn
        self._board = board
        self._win_state = win_state
        self._active_cell = active_cell

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self):
        return _repr(self)

    def copy(self) -> 'BoardState':
        return BoardState(self._board.copy(), self._win_state.copy(), self._active_cell, self.turn)

    def play(self, move: Move, pid: int) -> Tuple['AbsBoardState', int]:
        new_board = self.copy()
        new_board._turn += 1

        tile = 3 * move[0][0] + move[0][1]
        sub_tile = 3 * move[1][0] + move[1][1]

        new_board._board[tile, sub_tile] = pid
        new_board._active_cell = sub_tile

        new_board._win_state[tile] = new_board._get_winner_of(new_board._board[tile])

        return new_board, ((pid + 1) % 2) + 1

    def get_legal_moves(self, pid=0):
        # if fist move or the active cell is full and any move can be taken
        if self._active_cell == -1 or self._win_state[self._active_cell] != 0:
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
        # tie
        if 0 not in section:
            return -1

        # winner
        diags = [section[0::4], section[2:8:2]]
        rows = [section[0 + (3 * i): 3 + (3 * i)] for i in range(3)]
        cols = [section[i::3] for i in range(3)]

        for line in diags + rows + cols:
            if (0 not in line) and (-1 not in line) and len(set(line)) == 1:
                return line[0]

        # not over
        return 0
