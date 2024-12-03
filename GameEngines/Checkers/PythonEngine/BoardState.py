from typing import Set, Iterator, Type
from enum import Enum
import numpy as np

from GameEngines import BaseBoardState, AbsSaveModule
from GameEngines.cache_utils import cache_moves
from GameEngines.Checkers.repr import _repr
from GameEngines.Checkers.SaveModule import CheckersSave
from GameEngines.Checkers.utilsTypes import *
import GameEngines.Checkers.PythonEngine.utils as utils

class PieceType(Enum):
    Single = 1
    King = 2,


class BoardState(BaseBoardState):
    """
    This class is the Python implementation of BoardState for the `Checkers` game.
    Rules for the game can be found online
    """

    _DEFAULT_SAVE_MOD = CheckersSave

    def __init__(self, *, save_module: Type[AbsSaveModule] = _DEFAULT_SAVE_MOD):
        super().__init__(save_module=save_module)

        self._board = utils.board_setup()
        self._cached_moves = None # The moves cached on a multi jump move

    def __eq__(self, other: 'BoardState') -> bool:
        return (
                np.array_equal(
                    self._board[self._board != 3],
                    other._board[other._board != 3]
                ) and
                self._cached_moves == other._cached_moves and
                self._turn == other._turn and
                self._curr_pid == other._curr_pid
        )

    @property
    def board(self) -> np.ndarray:
        return self._board

    def __repr__(self) -> str:
        return _repr(self)

    def play(self, global_move: Move) -> 'BoardState':
        new_state = self.copy()
        new_state._turn += 1

        move = self._to_local(global_move)

        # move the pawn and remove whatever is in its path
        beg_val = new_state._board[move[0]]
        xs = sorted([move[0][0], move[1][0]])
        ys = sorted([move[0][1], move[1][1]])
        new_state._board[xs[0]: xs[1] + 1, ys[0]: ys[1] + 1] = 0
        new_state._board[move[1]] = beg_val

        # change from 1 -> 2 on the end row
        if global_move[1][0] == [0, 7][self._curr_pid % 2]:
            if abs(beg_val) == PieceType.Single.value:
                new_state._board[move[1]] *= 2

        # If the played move is a capture, check if multi jump available
        is_capture = (xs[1] - xs[0] + ys[1] - ys[0]) > 1
        if is_capture:
            # If multi jump available, cache them for next step
            moves, _ = new_state._get_moves(new_state._board, move[1], True)
            if len(moves) > 0:
                new_state._cached_moves = set(self._from_local((move[1], d)) for d in moves)
                return new_state

        new_state._cached_moves = None
        new_state._curr_pid = (self._curr_pid % 2) + 1
        return new_state

    @cache_moves
    def get_legal_moves(self, *, cache=False) -> Set[Move]:
        if self._cached_moves is not None:
            return self._cached_moves.copy()

        pieces = (self._board > 0 if self._curr_pid == 1 else self._board < 0) & (self._board < 3)
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
            np.sum((self._board > 0) & (self._board < 3)),
            np.sum(self._board < 0)
        )

    def winner(self) -> int:
        p1, p2 = self.score()

        if p1 <= 0 or p2 <= 0:
            return 1 if p1 > 0 else 2

        if not self._has_moves():
            return (self._curr_pid % 2) + 1

        return 0

    def _has_moves(self) -> bool:
        pieces = (self._board > 0 if self._curr_pid == 1 else self._board < 0) & (self._board < 3)
        coords: Iterator[Coords] = zip(*pieces.nonzero())

        for coord in coords:
            moves, _ = self._get_moves(self._board, coord, False)
            if len(moves) > 0:
                return True
        return False


    @staticmethod
    def _from_local(move: Move) -> Move:
        return (
            (4 + int(move[0][0] - move[0][1]), int(move[0][0] + move[0][1]) - 3),  # x_res = (4 + x - y)
            (4 + int(move[1][0] - move[1][1]), int(move[1][0] + move[1][1]) - 3)   # y_res = (x + y - 3)
        )

    @staticmethod
    def _to_local(move: Move) -> Move:
        return (
            (int(move[0][0] + move[0][1] - 1) // 2, int(move[0][1] - move[0][0] + 7) // 2),  # x_res = (x + y - 1) // 2
            (int(move[1][0] + move[1][1] - 1) // 2, int(move[1][1] - move[1][0] + 7) // 2)   # y_res = (y - x + 7) // 2
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
