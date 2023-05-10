import GameEngines
from GameEngines.UltiTTT.repr import _repr
BoardState = GameEngines.UltiTTT.RawUltiTTTState




# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr

