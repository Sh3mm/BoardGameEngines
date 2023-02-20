from GameEngines.Avalam import BoardState as RustBoardState
from GameEngines.Avalam.PythonEngine import BoardState as PyBoardState

import var_test
import numpy as np
import pytest


rust_python = pytest.mark.parametrize(
    "board_state",
    [RustBoardState, PyBoardState] if RustBoardState is not PyBoardState else [PyBoardState]
)


@rust_python
def test_init(board_state):
    b = board_state()
    assert b.turn == 0
    assert len(b.get_legal_moves()) == 292
    assert b.score() == (24, 24)
    assert np.sum(b.board) == 0
    assert b.board[3, 3] == 1
    assert b.board[3, 2] == -1
    assert b.board[1, 0] == 0


@rust_python
def test_play_from_init(board_state):
    b = board_state()
    b = b.play(((3, 8), (3, 7)))
    b = b.play(((3, 7), (3, 6)))
    b = b.play(((3, 6), (3, 5)))
    b = b.play(((3, 5), (3, 4)))
    b = b.play(((3, 3), (3, 2)))
    b = b.play(((3, 2), (3, 1)))
    b = b.play(((3, 1), (2, 1)))
    b = b.play(((2, 1), (1, 1)))

    assert b.board[1, 1] == 5
    assert b.board[3, 4] == -5
    assert b.board[3, 5] == 0
    assert b.board[3, 1] == 0
    assert b.get_legal_moves() == var_test.test_play_from_init_moves_avalam


@rust_python
def test_score(board_state):
    b = board_state()
    assert b.score() == (24, 24)

    b = b.play(((3, 8), (3, 7)))
    assert b.score() == (23, 24)

    b = b.play(((3, 7), (3, 6)))
    assert b.score() == (23, 23)
