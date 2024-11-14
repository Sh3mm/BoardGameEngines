from GameEngines.Checkers import BoardState as RustBoardState
from GameEngines.Checkers.PythonEngine import BoardState as PyBoardState

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
    assert len(b.get_legal_moves()) == 7


@rust_python
def test_play_from_init_1(board_state):
    b = board_state()
    moves = [
        ((5, 0), (4, 1)), ((2, 7), (3, 6)), ((1, 6), (2, 7)), ((5, 2), (4, 3)), ((0, 5), (1, 6)), ((6, 2), (5, 1)),
        ((2, 1), (3, 2)), ((7, 2), (6, 1)), ((1, 0), (2, 1)), ((5, 4), (4, 5)),
    ]
    for m in moves:
        b = b.play(m)

    assert b.curr_pid == 1

    b = b.play(((3, 6), (5, 4)))

    ref_board = board_state.load("test_files/test_checkers/from_init_board_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0

@rust_python
def test_to_king(board_state):
    b = board_state.load("test_files/test_checkers/from_init_board_1.json")
    moves = [((5, 4), (7, 2))]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_checkers/to_king_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0

@rust_python
def test_winner_elimination(board_state):
    b = board_state.load("test_files/test_checkers/winner_elimination_1.json")
    assert b.winner() == 0

    b = b.play(((4, 3), (2, 1)))
    assert b.winner() == 2

@rust_python
def test_winner_no_move(board_state):
    b = board_state.load("test_files/test_checkers/winner_no_move_1.json")
    assert b.winner() == 0

    b = b.play(((5, 6), (7, 4)))
    assert b.winner() == 1
