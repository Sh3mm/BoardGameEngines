from rust_engine import BoardState, gen_moves
from time import time

x = BoardState()

beg = time()
x.moves = gen_moves(x.board)
print(time() - beg)
print(len(x.moves))

beg = time()
z2 = x.get_legal_moves()
z = x.count()
print(time() - beg)

beg = time()
x.stack((1, 1), (1, 2))
print(time() - beg)

print(x)
