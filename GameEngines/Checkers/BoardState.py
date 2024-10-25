import GameEngines
from GameEngines.Checkers.repr import _repr
BoardState = GameEngines.Checkers.RawCheckersState


# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr
