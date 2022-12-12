from typing import Tuple, Union
import numpy as np
from avalamEngine import BoardState
from avalamEngine.utils import gen_moves


RATIO_PLACE_HOLDER = np.ones((9, 9, 2))


class Board:
    def __init__(self, raw_board, max_height: int):
        self.init_board = raw_board
        self.shape: Tuple[int, int] = raw_board[0].shape
        self.max_height = max_height
        self.base_moves = gen_moves(raw_board[0], self.max_height)

    def base_state(self):
        return BoardState(self, self.init_board, self.base_moves)

    def state_from(self, raw_board: Tuple[np.ndarray, np.ndarray]) -> BoardState:
        return BoardState(self, raw_board, gen_moves(raw_board[0], self.max_height))

    def ratio_from(self, prev_state: Union[BoardState, None], raw_board: np.ndarray):
        if prev_state is None:
            return self.init_board[1]

        dif = list(zip(*(abs(prev_state.board) - abs(raw_board)).nonzero()))
        origin, dest = dif if raw_board[dif[0]] == 0 else dif[::-1]
        state = prev_state.stack(origin, dest, no_move=True)

        return state.ratios
