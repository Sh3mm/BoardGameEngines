from typing import Set, List
import numpy as np

from GameEngines._generic import AbsBoardState
from GameEngines.Checkers.repr import _repr
from GameEngines.Checkers.utilsTypes import *
import GameEngines.Checkers.PythonEngine.utils as utils


class BoardState(AbsBoardState):
    """
    This class is the Python implementation of BoardState for the `Checkers` game.
    Rules for the game can be found online
    """

    def __init__(self, board: np.ndarray = None, turn: int = None, cached_moves: Set[Move] = None):
        if True in [c is None for c in [board, turn]]:
            turn = 0
            board = utils.board_setup()
            cached_moves = None

        self._board = board
        self._turn = turn
        self._cached_moves = cached_moves

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self) -> str:
        return _repr(self)

    def copy(self) -> 'BoardState':
        new_state = BoardState(
            self._board.copy(),
            self._turn,
            self._cached_moves.copy() if self._cached_moves is not None else None,
        )
        return new_state

    def play(self, g_move: Move, pid: int) -> Tuple['AbsBoardState', int]:
        new_state = self.copy()
        move = self._to_local(g_move)

        # move the pawn and remove whatever is in its path
        beg_val = new_state._board[move[0]]
        xs = sorted([move[0][0], move[1][0]])
        ys = sorted([move[0][1], move[1][1]])
        new_state._board[xs[0]: xs[1] + 1, ys[0]: ys[1] + 1] = 0
        new_state._board[move[1]] = beg_val

        # change from 1 -> 2 on the end row
        if [g_move[1][0] == 0, g_move[1][0] == 7][pid % 2]:
            if abs(beg_val) == 1:
                new_state._board[move[1]] *= 2

        check = self._check_moves(new_state._board, move[1])
        if check[1]:
            self._cached_moves = set(self._from_local((move[1], d)) for d in check[0])
            return new_state, pid
        self._cached_moves = None
        return new_state, (pid % 2) + 1

    def get_legal_moves(self, pid) -> Set[Move]:
        if self._cached_moves is not None:
            return self._cached_moves.copy()

        pieces = self._board > 0 if pid == 1 else self._board < 0
        coords: List[Coords] = list(zip(*pieces.nonzero()))

        captures = []
        moves = []
        for coord in coords:
            destinations, capture_found = self._check_moves(self._board, coord, len(captures) > 0)
            iter_dest = (self._from_local((coord, d)) for d in destinations)
            if capture_found:
                captures.extend(iter_dest)
            else:
                moves.extend(iter_dest)
        return set(moves if len(captures) == 0 else captures)

    def score(self) -> Tuple[int, int]:
        return (
            np.sum(self._board > 0),
            np.sum(self._board < 0)
        )

    def winner(self) -> int:
        p1, p2 = self.score()

        if p1 > 0 and p2 > 0:
            return 0

        return 1 if p1 > 0 else 2

    @staticmethod
    def _from_local(move: Move) -> Move:
        return (
            (4 + move[0][0] - move[0][1], move[0][0] + move[0][1] - 3),  # x_res = (4 + x - y)
            (4 + move[1][0] - move[1][1], move[1][0] + move[1][1] - 3)   # y_res = (x + y - 3)
        )

    @staticmethod
    def _to_local(move: Move) -> Move:
        return (
            ((move[0][0] + move[0][1] - 1) // 2, (move[0][1] - move[0][0] + 7) // 2),  # x_res = (x + y - 1) // 2
            ((move[1][0] + move[1][1] - 1) // 2, (move[1][1] - move[1][0] + 7) // 2)   # y_res = (y - x + 7) // 2
        )

    @staticmethod
    def _check_moves(board: np.ndarray, pos: Coords, capture_found: bool = False) -> Tuple[list, bool]:
        val = board[pos]
        if abs(val) == 1:
            return BoardState._check_man_moves(board, pos, val, capture_found)
        else:
            return BoardState._check_king_moves(board, pos, val, capture_found)

    @staticmethod
    def _check_man_moves(board: np.ndarray, pos: Coords, val: int, capture_found: bool = False) -> Tuple[list, bool]:
        treated: np.ndarray = np.abs(board + val) - abs(val)
        directions = [
            ((0, -1), treated[pos[0], :pos[1]][:-3:-1],  1),
            ((0, +1), treated[pos[0], pos[1] + 1:][:2], -1),
            ((-1, 0), treated[:pos[0], pos[1]][:-3:-1], -1),
            ((+1, 0), treated[pos[0] + 1:, pos[1]][:2],  1),
        ]
        directions = [d[:2] for d in directions if len(d[1]) > 0 and np.sign(val) == d[2]]

        captures = [
            (pos[0] + 2 * c[0], pos[1] + 2 * c[1])
            for c, d in directions
            if len(d) > 1 and d[0] < 0 and d[1] == 0
        ]
        if len(captures) > 0 or capture_found:
            return captures, True
        else:
            return [(pos[0] + c[0], pos[1] + c[1]) for c, d in directions if d[0] == 0], False

    @staticmethod
    def _check_king_moves(board: np.ndarray, pos: Coords, val: int, capture_found: bool = False) -> Tuple[list, bool]:
        treated: np.ndarray = np.abs(board + val) - abs(val)
        directions = [
            ((0, -1), treated[pos[0], :pos[1]][::-1]),
            ((0, +1), treated[pos[0], pos[1] + 1:]),
            ((-1, 0), treated[:pos[0], pos[1]][::-1]),
            ((+1, 0), treated[pos[0] + 1:, pos[1]]),
        ]

        moves = []
        captures = []
        for c, d in directions:
            pieces = list(d.nonzero()[0])

            if len(pieces) == 0 or d[pieces[0]] > 0:
                continue

            if d[0] == 0:
                moves.append(c)

            pieces.append(len(d))
            captures.extend([(c[0] * i, c[1] * i) for i in range(pieces[0] + 2, pieces[1] + 1)])

        if len(captures) > 0 or capture_found:
            return captures, True
        else:
            return moves, False


if __name__ == '__main__':
    b = BoardState()
    b.board[~np.isnan(b.board)] = 0
    b.board[(0, 3)] = 1
    b.board[(3, 7)] = 1
    b.board[(1, 3)] = -1
    b.board[(2, 2)] = -1
    b.board[(4, 6)] = -1
    m = b.get_legal_moves(1)
    print(m)
    b, p = b.play(m.pop(), 1)
    print(p)
    m = b.get_legal_moves(p)
    print(m)
    b, p = b.play(m.pop(), 1)
    print(p)
    m = b.get_legal_moves(p)
    print(m)
    print(b)
    print(b.board)
