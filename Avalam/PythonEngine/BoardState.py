import re
import numpy as np
from colorama import Fore
from typing import Set
from itertools import product
import Avalam.PythonEngine.utils as utils
from Avalam.utilsTypes import *


class BoardState:
    INIT_INFO = utils.board_setup()
    INIT_MOVES = utils.gen_moves(utils.board_setup()[0])

    def __init__(self, board_info: Tuple[np.ndarray, np.ndarray] = None, moves: Set = None):
        if board_info is None:
            board_info = self.INIT_INFO
            moves = self.INIT_MOVES

        self.board, self.ratios = board_info
        self._moves = moves
        self._on_move_call = None

    def __repr__(self) -> str:
        err = re.sub(r'(\d{2,}|[6-9])', fr'{Fore.LIGHTRED_EX}\1{Fore.RESET}', self.board.__str__())
        neg = re.sub(r'(-[1-5])', fr'{Fore.LIGHTBLUE_EX}\1{Fore.RESET}', err)
        pos = re.sub(r'((?: | \[)[1-5])', fr'{Fore.LIGHTYELLOW_EX}\1{Fore.RESET}', neg)
        return pos

    def copy(self) -> 'BoardState':
        return BoardState((self.board.copy(), self.ratios.copy()), self._moves.copy())

    def play(self, origin: Coords, dest: Coords) -> 'BoardState':

        new_board = self.copy()

        top = new_board.board[origin]
        new_board.board[origin] = 0
        bottom = new_board.board[dest]
        new_board.board[dest] = (int(top > 0) * 2 - 1) * abs(bottom) + top

        new_board._update_ratios(origin, dest)

        new_board._on_move_call = (origin, dest)
        return new_board

    def _update_moves(self, origin: Coords, dest: Coords):
        for i, j in product(range(-1, 2), range(-1, 2)):
            self._moves.discard((origin, (origin[0] + i, origin[1] + j)))
            self._moves.discard(((origin[0] + i, origin[1] + j), origin))

        for i, j in product(range(-1, 2), range(-1, 2)):
            if not (0 <= dest[0] + i < 9 and
                    0 <= dest[1] + j < 9):
                continue
            if abs(self.board[dest]) + abs(self.board[(dest[0] + i, dest[1] + j)]) > 5:
                self._moves.discard(((dest[0] + i, dest[1] + j), dest))
                self._moves.discard((dest, (dest[0] + i, dest[1] + j)))

    def _update_ratios(self, origin: Coords, dest: Coords):
        self.ratios[:, dest[0], dest[1]] += self.ratios[:, origin[0], origin[1]]
        self.ratios[:, origin[0], origin[1]] = 0

    def get_legal_moves(self) -> Set[Move]:
        if self._on_move_call is not None:
            self._update_moves(*self._on_move_call)
            self._on_move_call = None
        return self._moves

    def count(self) -> Tuple[int, int]:
        return (
            (self.board > 0).sum(),
            (self.board < 0).sum()
        )

    def winner(self) -> int:
        # unfinished
        if len(self.get_legal_moves()) > 0:
            return -2

        p1, p2 = self.count()
        # tie
        if p1 == p1:
            return -1
        # winner
        return int(p1 < p2)



if __name__ == '__main__':
    b = BoardState()
    b = b.play((4, 5), (3, 5))
    print(b)
