import time
from GameEngines.UltiTTT import BoardState, Player


class UltiTTTGame:
    def __init__(self, p0: Player, p1: Player):
        self.players = [p0, p1]
        self.boardState = BoardState()

    def play(self, results=True):
        turn = 0
        history = []
        time_data = []
        if results:
            print(self.players[0].get_name(), 'vs', self.players[1].get_name())
        while self.boardState.winner() == 0:
            player = self.players[turn % 2]

            moves = self.boardState.get_legal_moves()

            beg = time.time()
            res = player.play(self.boardState, moves, turn % 2, turn)
            time_data.append(time.time() - beg)

            history.append(res)
            self.boardState = self.boardState.play(res, turn % 2)

            turn += 1

        winner = self.boardState.winner()
        if results:
            if winner == -1:
                print('Tied')
            else:
                print(f'winner is: player-{winner}')
            print(f'played turns: {turn}')

        return winner, (history, time_data)
