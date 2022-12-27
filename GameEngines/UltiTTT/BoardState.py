from typing import List
from itertools import product, zip_longest
from GameEngines.UltiTTT import Move
import numpy as np
from colorama import Fore


class BoardState:
    def __init__(self, board: np.ndarray = None, win_state: List[int] = None, active_cell=None, turn=None):
        if board is None or win_state is None or active_cell is None or turn is None:
            turn = 0
            board = np.zeros((9, 9), dtype=np.int8)
            win_state = [0] * 9
            active_cell = -1

        self.turn = turn
        self.board = board
        self._win_state = win_state
        self.active_cell = active_cell

    def __repr__(self):
        HORIZONTAL_LINE = '\n' + '\u2500' * 6 + '\u253C' + '\u2500' * 7 + '\u253C' + '\u2500' * 6 + '\n'

        def color(v: int) -> str:
            if v == 0:
                return '0'
            if v == 1:
                return f'{Fore.BLUE}1{Fore.RESET}'
            if v == 2:
                return f'{Fore.LIGHTYELLOW_EX}2{Fore.RESET}'
            return f'{Fore.RED}{v}{Fore.RESET}'

        lines = []
        for i, j in product(range(3), range(3)):
            line = []
            for k in range(3):
                line.append(' '.join(map(color, self.board[3*i + k, 3*j:3*j+3])))
            lines.append(' \u2502 '.join(line))

        output = []
        for i in range(3):
            output.append(lines[3 * i] + '\n' + lines[3 * i + 1] + '\n' + lines[3 * i + 2])
        return HORIZONTAL_LINE.join(output)

    def copy(self):
        return BoardState(self.board.copy(), self._win_state.copy(), self.active_cell, self.turn)

    def play(self, move: Move, pid: int):
        new_board = self.copy()
        new_board.turn += 1

        tile = 3 * move[0][0] + move[0][1]
        sub_tile = 3 * move[1][0] + move[1][1]

        new_board.board[tile, sub_tile] = pid
        new_board.active_cell = sub_tile

        new_board._win_state[tile] = new_board._get_winner_of(new_board.board[tile])

        return new_board

    def get_legal_moves(self):
        # if fist move or the active cell is full and any move can be taken
        if self.active_cell == -1 or self._win_state[self.active_cell] != 0:
            return [
                ((i // 3, i % 3), (j // 3, j % 3))
                for i, j in zip(*np.where(self.board == 0))
                if self._win_state[i] == 0
            ]

        # if space left in the active cell
        return [
            ((self.active_cell // 3, self.active_cell % 3), (j // 3, j % 3))
            for j in np.where(self.board[self.active_cell] == 0)[0]
        ]

    def winner(self) -> int:
        return self._get_winner_of(self._win_state)

    @staticmethod
    def _get_winner_of(section: List[int]) -> int:
        diags = [section[0::4], section[2:8:2]]
        rows = [section[0 + (3 * i): 3 + (3 * i)] for i in range(3)]
        cols = [section[i::3] for i in range(3)]

        # winner
        for line in diags + rows + cols:
            if (0 not in line) and len(set(line)) == 1:
                return line[0]

        # tie
        if 0 not in section:
            return -1

        # not over
        return 0