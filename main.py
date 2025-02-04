from timeit import timeit
from GameEngines.Quoridor import BoardState, MoveType, WallType
from GameEngines import Game, RandomPlayer


r1 = timeit(lambda: Game(  BoardState, RandomPlayer(), RandomPlayer()).play_full(), number=50)
print(r1)
# r2 = timeit(lambda: Game(PyBoardState, RandomPlayer(), RandomPlayer()).play_full(), number=1_000)
# print(r2)
