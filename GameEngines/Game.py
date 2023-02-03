from GameEngines._generic import AbsBoardState, AbsPlayer
import time


class Game:
    def __init__(self, board_class, p0: AbsPlayer, p1: AbsPlayer):
        self.players = [p0, p1]
        self.boardState: AbsBoardState = board_class()

    def play(self, results=True):
        history = []
        time_data = []
        if results:
            print(self.players[0].name, 'vs', self.players[1].name)

        while self.boardState.winner() == 0:
            turn = self.boardState.turn
            p_nb = turn % 2 + 1
            player = self.players[p_nb - 1]
            moves = self.boardState.get_legal_moves(p_nb)

            beg = time.time()
            res = player.play(self.boardState, moves, p_nb)
            time_data.append(time.time() - beg)

            history.append(res)
            self.boardState = self.boardState.play(res, p_nb)

        points = self.boardState.score()
        winner = self.boardState.winner()

        if results:
            if winner == -1:
                print(f'Tied: {points}')
            else:
                print(f'winner is: player-{winner} {points}')
            print(f'played turns: {self.boardState.turn}')
            print(f'Board:\n{self.boardState}')

        return winner, points, (history, time_data)
