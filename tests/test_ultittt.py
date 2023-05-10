from GameEngines.UltiTTT import BoardState as RustBoardState
from GameEngines.UltiTTT.PythonEngine import BoardState as PyBoardState

import numpy as np
from itertools import product
import pytest
from var_test import test_play_from_init_moves_ultittt

rust_python = pytest.mark.parametrize(
    "board_state",
    [RustBoardState, PyBoardState] if RustBoardState is not PyBoardState else [PyBoardState]
)


@rust_python
def test_init(board_state):
    b = board_state()
    assert b.turn == 0
    assert len(b.get_legal_moves()) == 81
    assert b.score() == (0, 0)
    assert np.sum(b.board) == 0


@rust_python
def test_play_from_init(board_state):
    b = board_state()

    for i, j in product(range(3), range(3)):
        if (i, j) == (1, 1):
            continue
        b.play(((1, 1), (i, j)), 1)

    b.play(((1, 1), (1, 1)), 2)

    assert b.get_legal_moves() == test_play_from_init_moves_ultittt
