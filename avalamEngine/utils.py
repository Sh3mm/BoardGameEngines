import numpy as np
from itertools import product
from functools import reduce
from typing import Tuple, Dict, List

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]
VOIDS = [(0, 4), (6, 10), (15, 18), (25, 27), (34, 37), (40, 41), (44, 47), (54, 56), (63, 66), (71, 75), (77, 81)]
AUTO_BEST_MOVE = "auto_best"
NEED_TO_EXPLORE = "explore with minimax"


def board_setup(rows: int, lines: int) -> Tuple[np.ndarray, np.ndarray]:
    board = np.ones(rows * lines, int)
    board[1::2] = -1
    board[0:4] = 0
    for v1, v2 in VOIDS:
        board[v1:v2] = 0

    board = board.reshape((rows, lines)).T

    ratio = np.zeros((*board.shape, 2), int)
    ratio[:, :, 0] = board == 1
    ratio[:, :, 1] = board == -1

    return board.reshape((rows, lines)), ratio.reshape((rows, lines, 2))


def gen_moves(board: np.ndarray, max_height):
    moves = set()
    lines, rows = board.shape
    for i, j in product(range(lines), range(rows)):
        if board[i, j] == 0:
            continue
        pos = np.absolute(board[max(i - 1, 0): min(i + 2, lines), max(j - 1, 0): min(j + 2, rows)])
        legit = np.where((pos != 0) & (pos + abs(board[i, j]) <= max_height))
        legit = zip(
            legit[0] - (1 if i != 0 else 0) + i,
            legit[1] - (1 if j != 0 else 0) + j
        )

        def accumulate(acc: set, val: Coords):
            if val != (i, j):
                acc.add(((i, j), val))
            return acc

        reduce(accumulate, legit, moves)
    return moves


def gen_classified_moves(board: np.ndarray, max_height, current_player: int) -> Dict[str, List[Move]]:
    tower_moves: set[Move] = set()
    ok_moves: set[Move] = set()
    lines, rows = board.shape
    for i, j in product(range(lines), range(rows)):
        if board[i, j] == 0:
            continue
        pos = np.array(board[max(i - 1, 0): min(i + 2, lines), max(j - 1, 0): min(j + 2, rows)])

        if current_player ==0:
            current_player = -1
        tower = np.where((pos != 0) & (abs(pos) + abs(board[i, j]) == max_height) & (pos *current_player >0) & (board[i, j] * current_player<0))
        tower = zip(
            tower[0] - (1 if i != 0 else 0) + i,
            tower[1] - (1 if j != 0 else 0) + j
        )
        legit = np.where((pos != 0) & (abs(pos) + abs(board[i, j]) < max_height))
        legit = zip(
            legit[0] - (1 if i != 0 else 0) + i,
            legit[1] - (1 if j != 0 else 0) + j
        )

        def accumulate(acc: set[Move], val: Coords):
            if val != (i, j):
                acc.add(((i, j), val))
            return acc

        reduce(accumulate, tower, tower_moves)
        reduce(accumulate, legit, ok_moves)
    return {AUTO_BEST_MOVE: list(tower_moves), NEED_TO_EXPLORE: list(ok_moves)}


if __name__ == '__main__':
    board_setup(9, 9)
