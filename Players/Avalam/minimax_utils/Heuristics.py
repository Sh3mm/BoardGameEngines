from itertools import product
import numpy as np
from GameEngines.Avalam import BoardState


def board_pawn_diff(state: BoardState, pid: int):
    count = state.count()
    return count[pid] - count[1 - pid]


def ratio_points(state: BoardState, pid: int):
    self_keep, other_keep = (state.board > 0, state.board < 0) if pid == 0 else (state.board < 0, state.board > 0)
    self_ratio = state.board[self_keep] / state.ratios[pid, self_keep]
    other_ratio = state.board[other_keep] / state.ratios[1 - pid, other_keep]

    self_points = abs(self_ratio.sum())
    other_points = abs(other_ratio.sum())

    return self_points, other_points


def sure_points(state: BoardState, pid: int):
    base = np.abs(state.board)
    non_zero = base != 0
    mobile = (base < 5) & non_zero

    points = {(i, j): v for i, j, v in zip(*mobile.nonzero(), base[mobile])}
    active = set()
    for point in points:
        if point in active:
            continue

        next_to = [
            (point[0] + i, point[1] + j) for i, j in product(range(-1, 2), range(-1, 2))
            if(not (i == j == 0) and
               9 > point[0] + i >= 0 and 9 > point[1] + j >= 0 and
               (point[0] + i, point[1] + j) in points)
        ]
        active_next = [(i, j) for i, j in next_to if points[(i, j)] + points[point] < 5]
        if len(active_next) > 0:
            active_next.append(point)

        active.update(active_next)

    active.update(zip(*(base < 5).nonzero()))
    isolated_vals = state.board.take([9 * i + j for i, j in set(points.keys()) - active])

    if pid == 0:
        self_points, other_points = np.sum(isolated_vals > 0), np.sum(isolated_vals < 0)
    else:
        self_points, other_points = np.sum(isolated_vals < 0), np.sum(isolated_vals > 0)

    return self_points, other_points


def ratio_diff(state: BoardState, pid: int):
    self_p, other_p = ratio_points(state, pid)
    return self_p - other_p


def sure_ratio_dif(state: BoardState, pid: int):
    self_rp, other_rp = ratio_points(state, pid)
    self_sp, other_sp = sure_points(state, pid)
    return self_sp + self_rp / 4 - (self_sp + other_rp / 4)


if __name__ == '__main__':
    b = BoardState()
