from GameEngines.UltiTTT import BoardState

import numpy as np
from itertools import product
from var_test import test_play_from_init_moves_ultittt


def test_init():
    b = BoardState()
    assert b.turn == 0
    assert len(b.get_legal_moves()) == 81
    assert b.score() == (0, 0)
    assert np.sum(b.board) == 0


def test_play_from_init():
    b = BoardState()

    for i, j in product(range(3), range(3)):
        if (i, j) == (1, 1):
            continue
        b.play(((1, 1), (i, j)), 1)

    b.play(((1, 1), (1, 1)), 2)

    assert b.get_legal_moves() == test_play_from_init_moves_ultittt