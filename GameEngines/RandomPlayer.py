from GameEngines import AbsPlayer, AbsBoardState
from random import choice


class RandomPlayer(AbsPlayer):
    def __init__(self, p_name: str = None):
        self.name = p_name

    def play(self, board: AbsBoardState, moves: set, pid: int):
        return choice(list(moves))
