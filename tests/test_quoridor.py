from GameEngines.Quoridor import BoardState as RustBoardState
from GameEngines.Quoridor.PythonEngine import BoardState as PyBoardState
from GameEngines.Quoridor import PlayerInfo, MoveType as Mt, WallType as Wt

import numpy as np
import pytest


rust_python = pytest.mark.parametrize(
    "board_state",
    [RustBoardState, PyBoardState] if RustBoardState is not PyBoardState else [PyBoardState]
)

@rust_python
def test_init_no_param(board_state):
    b = board_state()
    assert b.turn == 0
    assert len(b.get_legal_moves()) == 131
    assert b.score() == (0, 0)
    assert b.board == (set(), (PlayerInfo((0, 4), 10), PlayerInfo((8, 4), 10)))

@rust_python
def test_init_with_param(board_state): # TODO: Change when b_size correctly implemented
    b = board_state(b_size=9, max_wall=5)
    assert b.turn == 0
    assert len(b.get_legal_moves()) == 131
    assert b.score() == (0, 0)
    assert b.board == (set(), (PlayerInfo((0, 4), 5), PlayerInfo((8, 4), 5)))

@rust_python
def test_play_from_init_1(board_state):
    b = board_state()
    moves = [
        (Mt.JUMP, ((0,4), (1,4))), (Mt.JUMP, ((8,4), (8,3))), (Mt.WALL, (Wt.H, (2, 2))), (Mt.JUMP, ((8,3), (7,3))),
        (Mt.JUMP, ((1,4), (2,4))), (Mt.JUMP, ((7,3), (6,3))), (Mt.JUMP, ((2,4), (3,4))), (Mt.JUMP, ((6,3), (5,3))),
        (Mt.JUMP, ((3,4), (4,4))), (Mt.JUMP, ((5,3), (4,3))), (Mt.JUMP, ((4,4), (5,4))), (Mt.JUMP, ((4,3), (3,3))),
        (Mt.JUMP, ((5,4), (6,4))),
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_quoridor/play_from_init_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0


@rust_python
def test_play_from_init_2(board_state):
    b = board_state()
    moves = [
        (Mt.JUMP, ((0,4), (1,4))), (Mt.JUMP, ((8,4), (7,4))), (Mt.JUMP, ((1,4), (2,4))), (Mt.JUMP, ((7,4), (6,4))),
        (Mt.JUMP, ((2,4), (3,4))), (Mt.JUMP, ((6,4), (5,4))), (Mt.JUMP, ((3,4), (4,4))), (Mt.JUMP, ((5,4), (3,4))),
        (Mt.JUMP, ((4,4), (5,4))), (Mt.JUMP, ((3,4), (2,4))), (Mt.JUMP, ((5,4), (6,4))), (Mt.JUMP, ((2,4), (1,4))),
        (Mt.JUMP, ((6,4), (7,4))), (Mt.JUMP, ((1,4), (0,4))),
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_quoridor/play_from_init_2.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 2


@rust_python
def test_wall_positions_1(board_state):
    b = board_state()
    moves = [
        (Mt.WALL, (Wt.V, (0, 0))), (Mt.WALL, (Wt.H, (0, 1))), (Mt.WALL, (Wt.V, (1, 1))), (Mt.WALL, (Wt.H, (1, 0))),
        (Mt.WALL, (Wt.V, (3, 1))), (Mt.WALL, (Wt.V, (5, 1))), (Mt.WALL, (Wt.V, (7, 1))), (Mt.WALL, (Wt.H, (6, 2))),
        (Mt.WALL, (Wt.H, (6, 4))), (Mt.WALL, (Wt.H, (6, 6))), (Mt.WALL, (Wt.V, (4, 6))), (Mt.WALL, (Wt.H, (3, 7))),
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_quoridor/wall_positions_1.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0


@rust_python
def test_wall_positions_2(board_state):
    b = board_state()
    moves = [
        (Mt.WALL, (Wt.V, (0, 0))), (Mt.WALL, (Wt.H, (0, 1))), (Mt.WALL, (Wt.V, (1, 1))), (Mt.WALL, (Wt.H, (1, 0))),
        (Mt.WALL, (Wt.V, (4, 4))), (Mt.WALL, (Wt.H, (4, 5))), (Mt.WALL, (Wt.V, (5, 5))), (Mt.WALL, (Wt.H, (5, 4))),
        (Mt.WALL, (Wt.V, (2, 2))), (Mt.WALL, (Wt.H, (2, 3))), (Mt.WALL, (Wt.V, (3, 3))), (Mt.WALL, (Wt.H, (3, 2))),
        (Mt.WALL, (Wt.H, (3, 4))), (Mt.WALL, (Wt.H, (4, 7))),
    ]

    for m in moves:
        b = b.play(m)

    ref_board = board_state.load("test_files/test_quoridor/wall_positions_2.json")

    assert b == ref_board
    assert b.get_legal_moves() == ref_board.__move_cache
    assert b.winner() == 0


@rust_python
def test_winner(board_state):
    b = board_state()
    assert b.winner() == 0

    ref_board = board_state.load("test_files/test_quoridor/winner_board_1.json")
    assert ref_board.winner() == 2

    ref_board = board_state.load("test_files/test_quoridor/winner_board_2.json")
    assert ref_board.winner() == 1
