import numpy as np
from colorama import Fore
import re
from itertools import product, chain
from typing import Tuple, Set
from copy import copy

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]


class BoardState:
    def __init__(self, base_board, board_info: Tuple[np.ndarray, np.ndarray], moves: Set, no_move=False):
        self.base_board = base_board
        self.board, self.ratios = board_info
        self.moves = moves
        self.no_move = no_move

    def __repr__(self) -> str:
        err = re.sub(r'(\d{2,}|[6-9])', fr'{Fore.LIGHTRED_EX}\1{Fore.RESET}', self.board.__str__())
        neg = re.sub(r'(-[1-5])', fr'{Fore.LIGHTBLUE_EX}\1{Fore.RESET}', err)
        pos = re.sub(r'((?: | \[)[1-5])', fr'{Fore.LIGHTYELLOW_EX}\1{Fore.RESET}', neg)
        return pos

    def copy(self) -> 'BoardState':
        return BoardState(self.base_board, (self.board.copy(), self.ratios.copy()), copy(self.moves))

    def stack(self, origin: Coords, dest: Coords, no_move=False) -> 'BoardState':
        if self.no_move:
            raise PermissionError("can't create a State from no_move state")

        new_board = self.copy()
        new_board.no_move = no_move

        top = new_board.board[origin]
        new_board.board[origin] = 0
        bottom = new_board.board[dest]
        new_board.board[dest] = (int(top > 0) * 2 - 1) * abs(bottom) + top

        new_board._update_ratios(origin, dest)
        if not no_move:
            new_board._update_moves(origin, dest)
        return new_board

    def _update_moves(self, origin: Coords, dest: Coords):
        for i, j in product(range(-1, 2), range(-1, 2)):
            self.moves.discard((origin, (origin[0] + i, origin[1] + j)))
            self.moves.discard(((origin[0] + i, origin[1] + j), origin))

        for i, j in product(range(-1, 2), range(-1, 2)):
            if not (0 <= dest[0] + i < self.base_board.shape[0] and
                    0 <= dest[1] + j < self.base_board.shape[1]):
                continue
            if abs(self.board[dest]) + abs(self.board[(dest[0] + i, dest[1] + j)]) > self.base_board.max_height:
                self.moves.discard(((dest[0] + i, dest[1] + j), dest))
                self.moves.discard((dest, (dest[0] + i, dest[1] + j)))

    def _update_ratios(self, origin: Coords, dest: Coords):
        self.ratios[dest] += self.ratios[origin]
        self.ratios[origin] = 0

    def get_legal_moves(self) -> Set[Move]:
        if self.no_move:
            raise PermissionError("can't get legal moves from no_move state")
        return self.moves

    def count(self) -> Tuple[int, int]:
        return (
            (self.board > 0).sum(),
            (self.board < 0).sum()
        )


if __name__ == '__main__':
    b = BoardState()
    b = b.stack((4, 5), (3, 5))
    print(b)
