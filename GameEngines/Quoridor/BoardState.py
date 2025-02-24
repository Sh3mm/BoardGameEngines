import GameEngines
from GameEngines.Quoridor.repr import _repr
from GameEngines.cache_utils import cache_moves, ignore_cache

BoardState = GameEngines.UltiTTT.RawQuoridorState


# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr

BoardState.get_legal_moves = cache_moves(BoardState.get_legal_moves)
BoardState.copy = ignore_cache(BoardState.copy)