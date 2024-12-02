from GameEngines.UltiTTT import BoardState as RustBoardState
from GameEngines.UltiTTT.PythonEngine import BoardState as PyBoardState

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
    assert len(b.get_legal_moves()) == 81
    assert b.score() == (0, 0)
    assert np.sum(b.board) == 0


@rust_python
def test_play_from_init_1(board_state):
    b = board_state()
    moves = [
        ((1, 1),(1, 1)), ((1, 1),(1, 2)), ((1, 2),(1, 1)), ((1, 1),(2, 2)), ((2, 2),(1, 1)), ((1, 1),(0, 2)),
        ((0, 2),(1, 1))
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_ultittt/from_init_board_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0

@rust_python
def test_play_from_init_2(board_state):
    b = board_state()
    moves = [
        ((0, 0),(0, 1)), ((0, 1),(0, 2)), ((0, 2),(1, 2)), ((1, 2),(2, 2)), ((2, 2),(2, 1)),
        ((2, 1),(2, 0)), ((2, 0),(1, 0)), ((1, 0),(1, 1)), ((1, 1),(1, 1)),
        ((1, 1),(0, 2)), ((0, 2),(1, 0)), ((1, 0),(2, 0)), ((2, 0),(2, 0)), ((2, 0),(1, 1)),
        ((1, 1),(2, 2)), ((2, 2),(0, 2)), ((0, 2),(1, 1)), ((1, 1),(2, 0)), ((2, 0),(0, 0)),
        ((0, 0),(1, 1)), ((1, 1),(0, 0))
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_ultittt/from_init_board_2.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 1

@rust_python
def complete_to_same(board_state):
    b = board_state()
    moves = [
        ((1, 1),(0, 0)), ((0, 0), (1, 1)), ((1, 1),(2, 2)), ((2, 2), (1, 1)), ((1, 1),(1, 1))
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_ultittt/complete_to_same_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 1
@rust_python
def test_winner(board_state):
    b = board_state()
    assert b.winner() == 0

    ref_board = board_state.load("test_files/test_ultittt/winner_board_1.json")
    assert ref_board.winner() == 2

    ref_board = board_state.load("test_files/test_ultittt/winner_board_2.json")
    assert ref_board.winner() == 1

    ref_board = board_state.load("test_files/test_ultittt/winner_board_3.json")
    assert ref_board.winner() == -1