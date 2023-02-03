import numpy as np
from itertools import product
from functools import reduce
from typing import Tuple

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]
VOIDS = [(0, 4), (6, 10), (15, 18), (25, 27), (34, 37), (40, 41), (44, 47), (54, 56), (63, 66), (71, 75), (77, 81)]


def board_setup() -> Tuple[np.ndarray, np.ndarray]:
    """
    method used to create a new raw (ndarray) board for the Avalam game

    :return: a ndarray of the initial board
    """
    board = np.ones(81, int)
    board[1::2] = -1
    board[0:4] = 0
    for v1, v2 in VOIDS:
        board[v1:v2] = 0

    board = board.reshape((9, 9)).T

    ratio = np.zeros((2, *board.shape), int)
    ratio[0, :, :] = board == 1
    ratio[1, :, :] = board == -1

    return board.reshape((9, 9)), ratio.reshape((2, 9, 9))


def gen_moves(board: np.ndarray):
    """
    method used to generate the current possible moves of a raw (ndarray) board of the Avalam game

    :param board: the raw board of an Avalam game
    :return: a set of legal moves for the given board
    """
    moves = set()
    lines, rows = board.shape
    for i, j in product(range(lines), range(rows)):
        if board[i, j] == 0:
            continue
        pos = np.absolute(board[max(i - 1, 0): min(i + 2, lines), max(j - 1, 0): min(j + 2, rows)])
        legit = np.where((pos != 0) & (pos + abs(board[i, j]) <= 5))
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

