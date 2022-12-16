import re
from colorama import Fore
from typing import Tuple

import GameEngines


class BoardState(GameEngines.Avalam.RawAvalamState):
    def __repr__(self):
        err = re.sub(r'(\d{2,}|[6-9])', fr'{Fore.LIGHTRED_EX}\1{Fore.RESET}', self.board.__str__())
        neg = re.sub(r'(-[1-5])', fr'{Fore.LIGHTBLUE_EX}\1{Fore.RESET}', err)
        pos = re.sub(r'((?: | \[)[1-5])', fr'{Fore.LIGHTYELLOW_EX}\1{Fore.RESET}', neg)
        return pos

    def count(self) -> Tuple[int, int]:
        return (self.board > 0).sum(), (self.board < 0).sum()

    def winner(self) -> int:
        # unfinished
        if len(self.get_legal_moves()) > 0:
            return -2

        p1, p2 = self.count()
        # tie
        if p1 == p1:
            return -1
        # winner
        return int(p1 < p2)
