import re
from colorama import Fore
from .rust_engine import *

__doc__ = rust_engine.__doc__
if hasattr(rust_engine, "__all__"):
    __all__ = rust_engine.__all__


def board_repr(self):
    err = re.sub(r'(\d{2,}|[6-9])', fr'{Fore.LIGHTRED_EX}\1{Fore.RESET}', self.board.__str__())
    neg = re.sub(r'(-[1-5])', fr'{Fore.LIGHTBLUE_EX}\1{Fore.RESET}', err)
    pos = re.sub(r'((?: | \[)[1-5])', fr'{Fore.LIGHTYELLOW_EX}\1{Fore.RESET}', neg)
    return pos


def count(self):
    return (self.board > 0).sum(), (self.board < 0).sum()


BoardState.__repr__ = board_repr
BoardState.get_legal_moves = lambda self: self.moves
BoardState.count = count
