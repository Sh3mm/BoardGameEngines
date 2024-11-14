from typing import Type, List, Any
import time
import math
from GameEngines.abstract import AbsBoardState, AbsPlayer


class Game:
    """
    This Class represents a game between two AbsPlayer agent.
    It can play any game implementing AbsBoardState
    """
    def __init__(self, board_class: Type[AbsBoardState], p0: AbsPlayer, p1: AbsPlayer):
        self.players = [p0, p1]

        self.board_class = board_class
        self.history: List[AbsBoardState] = [board_class()]
        self.move_history: List[Any] = []
        self.time_data: List[float] = []

        self.winner = 0

    def __repr__(self) -> str:
        last_move = self.move_history[-1] if len(self.move_history) > 0 else '-'
        last_move_str = f"\nLast move: {last_move}"

        player_text = (
            f"\nWinner: {self.winner}\n"
            if self.winner != 0 else
            f"\nNext player: {self.history[-1].curr_pid}"
        )

        return self.history[-1].__repr__() + last_move_str + player_text

    def play_full(self):
        """
        the play_full method plays a full game and returns the results

        :return: the winner, the final score and move data
        """
        self.play(math.inf)

    def play(self, n=1):
        """
        the play method will play the next n turns of the game

        :param n: the number of turns to be played
        """
        played = 0
        while self.winner == 0 and played < n:
            p_nb = self.history[-1].curr_pid
            player = self.players[p_nb - 1]
            moves = self.history[-1].get_legal_moves()

            beg = time.time()
            move = player.play(self.history[-1], moves, p_nb)
            self.time_data.append(time.time() - beg)

            next_step = self.history[-1].play(move)

            self.move_history.append(move)
            self.history.append(next_step)

            self.winner = self.history[-1].winner()
            played += 1

    def branch(self, i: int) -> 'Game':
        """
        This method creates a new game branching from a point in the game

        :param i: the turn after which the game will be forked
        :return: the forked game
        """
        i += 1
        new_game = Game(self.board_class, *self.players)
        new_game.history = self.history[:i]
        new_game.time_data = self.time_data[:i-1]
        new_game.winner = self.winner

        return new_game
