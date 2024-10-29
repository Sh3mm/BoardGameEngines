from GameEngines.UltiTTT import BoardState
from GameEngines import Game, RandomPlayer


g = Game(BoardState, RandomPlayer(), RandomPlayer())

while g.winner == 0:
    g.play()
    print(g.history[-1])
    print(g.winner)
