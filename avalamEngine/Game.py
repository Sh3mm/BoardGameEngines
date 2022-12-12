import time
from avalamEngine import Board, utils
from avalamEngine.Players import Player


class Game:
    def __init__(self, p0: Player, p1: Player):
        self.players = [p0, p1]
        board = Board(utils.board_setup(9, 9), 5)

        self.boardState = board.base_state()

    def play(self, results=True):
        turn = 0
        history = []
        time_data = []
        if results:
            print(self.players[0].name, 'vs', self.players[1].name)
        while True:
            player = self.players[turn % 2]

            moves = self.boardState.get_legal_moves()
            if len(moves) == 0:
                break

            beg = time.time()
            res = player.play(self.boardState, moves, turn % 2, turn)
            time_data.append(time.time() - beg)

            history.append(res)
            self.boardState = self.boardState.stack(*res)

            turn += 1

        points = self.boardState.count()
        winner = int(points[0] < points[1]) if points[0] != points[1] else -1
        if results:
            if winner == -1:
                print(f'Tied: {points}')
            else:
                print(f'winner is: player-{winner} {points}')
            print(f'played turns: {turn}')
            #print(f'Board:\n {self.boardState}')

        return winner, points, (history, time_data)
