import GameEngines
from GameEngines.Avalam.repr import _repr
BoardState = GameEngines.Avalam.RawAvalamState


# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr
