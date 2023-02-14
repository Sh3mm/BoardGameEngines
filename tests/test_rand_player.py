from GameEngines import RandomPlayer
from GameEngines.Avalam import BoardState as Avalam
from GameEngines.UltiTTT import BoardState as UltiTTT

import pytest


def test_player_init():
    player = RandomPlayer('test-name')
    assert player.name == 'test-name'


@pytest.mark.parametrize("board", [Avalam, UltiTTT])
def test_player_play(board):
    player = RandomPlayer('test-name')
    b = board()

    res = player.play(b, b.get_legal_moves(1), 1)

    assert res in b.get_legal_moves(1)
