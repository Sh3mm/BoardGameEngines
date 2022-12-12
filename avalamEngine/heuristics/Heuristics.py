import numpy as np
from avalamEngine import BoardState, Board, utils


def board_pawn_diff(state: BoardState, pid: int):
    count = state.count()
    return count[pid] - count[1 - pid]


def ratio_points(state: BoardState, pid: int):
    self_keep, other_keep = (state.board > 0, state.board < 0) if pid == 0 else (state.board < 0, state.board > 0)
    self_ratio = state.board[self_keep] / state.ratios[self_keep, pid]
    other_ratio = state.board[other_keep] / state.ratios[other_keep, 1 - pid]

    self_points = abs(self_ratio.sum())
    other_points = abs(other_ratio.sum())

    return self_points, other_points


def sure_points(state: BoardState, pid: int):
    base = np.abs(state.board)
    non_zero = base != 0
    mobile = (base < 5) & non_zero
    result = np.zeros((9, 9), bool)
    for i, j in zip(*mobile.nonzero()):
        if result[i, j]:
            continue
        around = np.ix_(range(max(0, i - 1), min(9, i + 2)), range(max(0, j - 1), min(9, j + 2)))
        res = (base[around] <= (5 - base[i, j])) & (non_zero[around])
        if np.sum(res) - (base[i, j] < 3):
            result[around] |= res
            result[i, j] = True
        else:
            result[i, j] = False

    cell_points = state.board[(result == False) & non_zero]
    self_cell = (cell_points > 0) if pid == 0 else (cell_points < 0)

    self_points = 1 + sum(6 - abs(cell_points[self_cell])) / 5
    other_points = 1 + sum(6 - abs(cell_points[self_cell == False])) / 5

    return self_points, other_points


def ratio_diff(state: BoardState, pid: int):
    self_p, other_p = ratio_points(state, pid)
    return self_p - other_p


def sure_ratio_dif(state: BoardState, pid: int):
    self_rp, other_rp = ratio_points(state, pid)
    self_sp, other_sp = sure_points(state, pid)
    return self_sp + self_rp / 4 - (self_sp + other_rp / 4)


if __name__ == '__main__':
    b = Board(utils.board_setup(4, 4), 5)
    s = b.base_state()
    s.board = np.zeros((4, 4))
    s.board[2, 3] = 3
    s.board[2, 2] = 2
    s.board[1, 1] = -1
    s.board[0, 1] = 1
    #s.board[0, 3] = -1
    print(s)
    print(sure_points(s, 0))
