from typing import Set, Iterator, Dict, Any
from enum import Enum
from copy import deepcopy
import numpy as np

from GameEngines._generic import AbsBoardState, cache_moves
from GameEngines.Checkers.repr import _repr
from GameEngines.Checkers.utilsTypes import *
import GameEngines.Checkers.PythonEngine.utils as utils

class PieceType(Enum):
    Single = 1
    King = 2,


class BoardState(AbsBoardState):
    """
    This class is the Python implementation of BoardState for the `Checkers` game.
    Rules for the game can be found online
    """

    def __init__(self):
        self._board = utils.board_setup()
        self._cached_moves = None
        self._turn = 0
        self._active_pid = 1

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def curr_pid(self) -> int:
        return self._active_pid

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self) -> str:
        return _repr(self)

    def copy(self) -> 'BoardState':
        return deepcopy(self)

    def play(self, global_move: Move) -> 'AbsBoardState':
        new_state = self.copy()
        move = self._to_local(global_move)

        # move the pawn and remove whatever is in its path
        beg_val = new_state._board[move[0]]
        xs = sorted([move[0][0], move[1][0]])
        ys = sorted([move[0][1], move[1][1]])
        new_state._board[xs[0]: xs[1] + 1, ys[0]: ys[1] + 1] = 0
        new_state._board[move[1]] = beg_val

        # change from 1 -> 2 on the end row
        if [global_move[1][0] == 0, global_move[1][0] == 7][self._active_pid % 2]:
            if abs(beg_val) == PieceType.Single.value:
                new_state._board[move[1]] *= 2

        # If the played move is a capture, check if multi jump available
        is_capture = (xs[1] - xs[0] + ys[1] - ys[0]) > 1
        if is_capture:
            # If multi jump available, cache them for next step
            check = new_state._get_moves(new_state._board, move[1])
            if check[1]:
                new_state._cached_moves = set(self._from_local((move[1], d)) for d in check[0])
                return new_state

        new_state._cached_moves = None
        new_state._active_pid = (self._active_pid % 2) + 1
        return new_state

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        if self._cached_moves is not None:
            return self._cached_moves.copy()

        pieces = self._board > 0 if self._active_pid == 1 else self._board < 0
        coords: Iterator[Coords] = zip(*pieces.nonzero())

        moves = []
        capture = False
        for coord in coords:
            destinations, _capture = self._get_moves(self._board, coord, capture)
            iter_dest = (self._from_local((coord, d)) for d in destinations)
            # If a capture is detected, drop normal moves and only keep captures
            if _capture and not capture:
                moves = []
                capture = True

            moves.extend(iter_dest)
        return set(moves)

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

    @classmethod
    def _load_data(cls, data: Dict[str, Any]) -> 'BoardState':
        new_board = BoardState()
        new_board._board = data["board"]
        new_board._cached_moves = data["cached_moves"]
        new_board._turn = data["turn"]
        new_board._active_pid = data["active_pid"]
        return new_board

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
    def _get_moves(board: np.ndarray, pos: Coords, capture_found: bool = False) -> Tuple[list, bool]:
        val = board[pos]
        piece_type, piece_sign = abs(val), np.sign(val)

        normalized: np.ndarray = board * piece_sign
        directions = [
            ((0, -1), normalized[pos[0], :pos[1]][:-3:-1],  1),
            ((0, +1), normalized[pos[0], pos[1] + 1:][:2], -1),
            ((-1, 0), normalized[:pos[0], pos[1]][:-3:-1], -1),
            ((+1, 0), normalized[pos[0] + 1:, pos[1]][:2],  1),
        ]
        # If the piece is not a king, only keep allowed diagonals
        if piece_type == PieceType.Single.value:
            directions = [d for d in directions if piece_sign == d[2]]

        # Filtering out directions if no adjacent spaces
        directions = [d[:2] for d in directions if len(d[1]) >= 1]

        # Getting the captures if there are any
        captures = [
            (pos[0] + 2 * c[0], pos[1] + 2 * c[1])
            for c, d in directions
            # If there is space for a jump, the next space is an enemy and the jump space is open,
            if len(d) >= 2 and d[0] < 0 and d[1] == 0
        ]
        if len(captures) > 0 or capture_found:
            return captures, True
        else:
            return [(pos[0] + c[0], pos[1] + c[1]) for c, d in directions if d[0] == 0], False


if __name__ == '__main__':
    b = BoardState()
    b.board[~np.isnan(b.board)] = 0
    b.board[(0, 3)] = 1
    b.board[(3, 7)] = 1
    b.board[(1, 3)] = -1
    b.board[(2, 2)] = -2
    b.board[(3, 6)] = -1
    print(b)
    m = b.get_legal_moves(1)
    print(m)
    b, p = b.play(m.pop(), 1)
    print(p)
    print(b)
    m = b.get_legal_moves(p)
    print(m)
    b, p = b.play(m.pop(), 1)
    print(p)
    print(b)
    m = b.get_legal_moves(p)
    print(m)
    print(b.board)
