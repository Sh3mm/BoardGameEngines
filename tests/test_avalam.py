from GameEngines.Avalam import BoardState as RustBoardState
from GameEngines.Avalam.PythonEngine import BoardState as PyBoardState

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
def test_play_from_init_1(board_state):
    b = board_state()
    moves = [
        ((3, 8), (3, 7)), ((3, 7), (3, 6)), ((3, 6), (3, 5)), ((3, 5), (3, 4)),
        ((3, 3), (3, 2)), ((3, 2), (3, 1)), ((3, 1), (2, 1)), ((2, 1), (1, 1))
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_avalam/from_init_board_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.get_legal_moves()
    assert b.winner() == 0

@rust_python
def test_play_from_init_2(board_state):
    b = board_state()
    moves = [
        ((0, 2), (1, 3)), ((1, 3), (2, 4)), ((2, 4), (3, 5)), ((3, 5), (4, 6)),
        ((2, 6), (3, 7)), ((3, 7), (4, 8)), ((4, 8), (5, 7)), ((5, 7), (6, 6)),
        ((7, 7), (8, 6)), ((8, 6), (7, 5)), ((7, 5), (6, 4)), ((5, 5), (6, 4)),
        ((6, 2), (5, 3)), ((5, 1), (4, 2)), ((5, 3), (4, 2)), ((4, 2), (3, 3)),
        ((4, 0), (3, 1)), ((3, 1), (2, 2)), ((2, 2), (1, 1)),
        ((0, 3), (1, 4)), ((1, 4), (2, 5)), ((2, 5), (3, 6)), ((3, 6), (4, 5)),
        ((3, 8), (4, 7)), ((4, 7), (5, 6)), ((5, 6), (6, 7)), ((6, 7), (7, 6)),
        ((8, 5), (7, 4)), ((7, 4), (6, 3)), ((6, 3), (5, 4)), ((5, 4), (6, 5)),
        ((5, 2), (4, 3)), ((4, 3), (3, 2)), ((3, 2), (4, 1)), ((4, 1), (5, 0)),
        ((2, 1), (1, 1)), ((2, 3), (3, 4))
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_avalam/from_init_board_2.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.get_legal_moves()
    assert b.winner() == 2


@rust_python
def test_play_from_save(board_state):
    b = board_state.load("test_files/test_avalam/from_save_board_1.json")
    moves = [
        ((1, 2),(2, 2)), ((3, 2),(3, 3)), ((3, 4),(2, 4)), ((2, 5),(3, 5)), ((3, 6),(4, 6)),
        ((6, 7),(5, 7)), ((5, 7),(4, 8)), ((7, 6),(7, 5)), ((5, 6),(6, 6)), ((6, 5),(5, 5)),
        ((5, 4),(6, 4)), ((6, 3),(5, 3)), ((4, 1),(5, 0)), ((4, 5),(4, 6)), ((5, 5),(6, 4)),
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_avalam/from_save_board_2.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.get_legal_moves()
    assert b.winner() == 2


@rust_python
def test_score(board_state):
    b = board_state()
    assert b.score() == (24, 24)

    b = b.play(((3, 8), (3, 7)))
    assert b.score() == (23, 24)

    b = b.play(((3, 7), (3, 6)))
    assert b.score() == (23, 23)
