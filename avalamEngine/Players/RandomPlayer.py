from avalamEngine import BoardState, Move
from avalamEngine.Players import Player
from typing import Set, Tuple
from random import choice


class RandomPlayer(Player):
    def __init__(self, p_name: str = None):
        self.name = p_name

    def play(self, board: BoardState, moves: Set[Move], pid: int, turn: int) -> Move:
        return choice(list(moves))
