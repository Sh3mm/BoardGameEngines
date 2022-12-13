from Avalam import Player, Move, BoardState
from typing import Set
from random import choice


class RandomPlayer(Player):
    def __init__(self, p_name: str = None):
        self.name = p_name

    def play(self, board: BoardState, moves: Set[Move], pid: int, turn: int) -> Move:
        return choice(list(moves))
