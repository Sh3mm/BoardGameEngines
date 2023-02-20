import re
from itertools import product

from colorama import Fore

import GameEngines
BoardState = GameEngines.UltiTTT.RawUltiTTTState


def _repr(self):
    HORIZONTAL_LINE = '\n' + '\u2500' * 6 + '\u253C' + '\u2500' * 7 + '\u253C' + '\u2500' * 6 + '\n'

    def color(v: int) -> str:
        if v == 0:
            return '0'
        if v == 1:
            return f'{Fore.BLUE}1{Fore.RESET}'
        if v == 2:
            return f'{Fore.LIGHTYELLOW_EX}2{Fore.RESET}'
        return f'{Fore.RED}{v}{Fore.RESET}'

    lines = []
    for i, j in product(range(3), range(3)):
        line = []
        for k in range(3):
            line.append(' '.join(map(color, self._board[3*i + k, 3*j:3*j+3])))
        lines.append(' \u2502 '.join(line))

    output = []
    for i in range(3):
        output.append(lines[3 * i] + '\n' + lines[3 * i + 1] + '\n' + lines[3 * i + 2])
    return HORIZONTAL_LINE.join(output)


# addition of the __repr__ method on the rust implementation of the class
BoardState.__repr__ = _repr

