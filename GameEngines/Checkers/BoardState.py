import GameEngines
from GameEngines.Checkers.repr import _repr
from GameEngines._generic import cache_moves

BoardState = GameEngines.Checkers.RawCheckersState


# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr

BoardState.get_legal_moves = cache_moves(BoardState.get_legal_moves)