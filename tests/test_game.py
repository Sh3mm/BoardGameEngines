from GameEngines import Game, RandomPlayer
from GameEngines.Avalam import BoardState as Avalam
from GameEngines.UltiTTT import BoardState as UltiTTT

import pytest

engines = [Avalam, UltiTTT]

all_games = pytest.mark.parametrize(
    "engine",
    [Avalam, UltiTTT]
)


@all_games
def test_game_init(engine):
    players = [RandomPlayer(), RandomPlayer()]
    game = Game(engine, *players)

    assert game.players == players
    assert len(game.history) == 1
    assert len(game.time_data) == 0
    assert game.winner == 0


@all_games
def test_play(engine):
    players = [RandomPlayer(), RandomPlayer()]
    game = Game(engine, *players)

    game.play()
    assert len(game.history) == 2
    assert len(game.time_data) == 1

    game.play(5)
    assert len(game.history) == 7
    assert len(game.time_data) == 6


@all_games
def test_play_all(engine):
    players = [RandomPlayer(), RandomPlayer()]
    game = Game(engine, *players)

    game.play_full()
    assert game.winner != 0
    assert len(game.history) - 1 == len(game.time_data)


@all_games
def test_branch(engine):
    players = [RandomPlayer(), RandomPlayer()]
    game = Game(engine, *players)

    game.play_full()
    ori_len = len(game.history)
    branch = game.branch(4)

    assert branch.history == game.history[:5]
    assert branch.time_data == game.time_data[:4]
    assert len(branch.time_data) == len(branch.history) - 1
    assert ori_len == len(game.history)
