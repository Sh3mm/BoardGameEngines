from typing import Tuple, List, Union, Set
import numpy as np
from itertools import chain

from GameEngines.Quoridor.utilsTypes import WallType, MoveType
from GameEngines.Quoridor.PythonEngine.pathfinding import dfs, best_fs


_Jump = Tuple[int, int]
_Wall = Tuple[WallType, int]
_Move = Tuple[MoveType, Union[_Wall, _Jump]]


def init_board(size: int) -> np.ndarray:
    board = np.zeros((4, size**2), int)
    board[0, :] = np.arange(-size, size**2 - size)  # Top
    board[1, :] = np.arange(size , size**2 + size)  # Down
    board[2, :] = np.arange(-1   , size**2 - 1)     # Left
    board[3, :] = np.arange( 1   , size**2 + 1)     # Right

    board[0, 0:size] = -1                           # First row has nothing over
    board[1, size**2-size:size**2] = -1             # Last  row has nothing below
    board[2, np.arange(0, size**2, size)] = -1      # First col has nothing to it's left
    board[3, np.arange(size-1, size**2, size)] = -1 # Last  col has nothing to it's right
    return board


def cut_wall(board: np.ndarray, wall: _Wall, *, inplace=False) -> np.ndarray:
    # creates a new board if inplace is set to false
    new_board = board if inplace else board.copy()

    new_board[(
        (1, 1, 0, 0) if wall[0] is WallType.H else (3, 2, 3, 2), # vertical or horizontal connection cut
        (wall[1], wall[1] + 1, wall[1] + 9, wall[1] + 10)
    )] = -1

    return new_board

def validate_walls(board, poses, new_walls: List[_Wall], old_walls: Set[_Wall]) -> List[_Wall]:
    to_check = set(new_walls)
    if len(old_walls) < 2:  # Cannot block a player with less than 3 walls
        return list(to_check)

    pid1, pid2 = 0, 1
    goals = [range(72, 81), range(0, 9)]

    paths = [dfs(board, poses[pid1], goals[pid1], pid1), dfs(board, poses[pid2], goals[pid2], pid2)]

    legit, to_check = _filter_pass(paths, to_check)

    for wall in to_check:
        is_legit = (
            dfs(cut_wall(board, wall), poses[pid1], goals[pid1], pid1) is not None and
            dfs(cut_wall(board, wall), poses[pid2], goals[pid2], pid2) is not None
        )
        if is_legit:
            legit.append(wall)

    return legit

def _filter_pass(paths, to_check: Set[_Wall]) -> Tuple[List[_Wall], Set[_Wall]]:

    pairs = set(
        [(min(v, paths[0][i+1]), abs(v - paths[0][i+1])) for i, v in enumerate(paths[0][:-1])] +
        [(min(v, paths[1][i+1]), abs(v - paths[1][i+1])) for i, v in enumerate(paths[1][:-1])]
    )
    prob_walls = set(chain(*[
        ((WallType.H, p[0]), (WallType.H, p[0] - 1))
        if p[1] == 9 else
        ((WallType.V, p[0]), (WallType.V, p[0] - 9))
        for p in pairs
    ]))

    legit = to_check.difference(prob_walls)
    return list(legit), to_check.difference(legit)

