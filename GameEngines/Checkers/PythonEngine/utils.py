import numpy as np


def board_setup():
    n = 3
    board = np.array([
        [ n, n, n, 1, 1, n, n, n],
        [ n, n, 0, 1, 1, 1, n, n],
        [ n,-1, 0, 0, 1, 1, 1, n],
        [-1,-1,-1, 0, 0, 1, 1, 1],
        [ n,-1,-1,-1, 0, 0, 1, n],
        [ n, n,-1,-1,-1, 0, n, n],
        [ n, n, n,-1,-1, n, n, n],
    ], dtype=int)
    return board
