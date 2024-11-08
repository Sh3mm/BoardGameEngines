from typing import Tuple, List

Coords = Tuple[int, int]
Move = Tuple[Coords, Coords]

def to_move(move: List[List[int]]) -> Move:
    return (move[0][0], move[0][1]), (move[1][0], move[1][1])
