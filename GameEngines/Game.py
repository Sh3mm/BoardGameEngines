from typing import Type, List
import time
import math
from GameEngines._generic import AbsBoardState, AbsPlayer


class Game:
    """
    This Class represents a game between two AbsPlayer agent.
    It can play any game implementing AbsBoardState
    """
    def __init__(self, board_class: Type[AbsBoardState], p0: AbsPlayer, p1: AbsPlayer):
        self.players = [p0, p1]

        self.board_class = board_class
        self.history: List[AbsBoardState] = [board_class()]
        self.time_data: List[float] = []

        self.winner = 0

    def play_full(self, results=True):
        """
        the play_full method plays a full game and returns the results

        :param results: Should the final board be shown in terminal
        :return: the winner, the final score and move data
        """
        self.play(math.inf)

    def play(self, n=1):
        played = 0
        while self.winner == 0 and played < n:
            turn = self.history[-1].turn
            p_nb = turn % 2 + 1
            player = self.players[p_nb - 1]
            moves = self.history[-1].get_legal_moves(p_nb)

            beg = time.time()
            res = player.play(self.history[-1], moves, p_nb)
            self.time_data.append(time.time() - beg)

            self.history.append(self.history[-1].play(res, p_nb))
            self.winner = self.history[-1].winner()
            played += 1

    def branch(self, i: int) -> 'Game':
        i += 1
        new_game = Game(self.board_class, *self.players)
        new_game.history = self.history[:i]
        new_game.time_data = self.time_data[:i]
        new_game.winner = self.winner

        return new_game

    def show_state(self):
        points = self.history[-1].score()
        if self.winner == -1:
            print(f'Tied: {points}')
        elif self.winner != 0:
            print(f'winner is: player-{self.winner} {points}')
        else:
            print('Game is ongoing')
        print(f'played turns: {self.history[-1].turn}')
        print(f'Board:\n{self.history[-1]}')
