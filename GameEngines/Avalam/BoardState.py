import re
from colorama import Fore

import GameEngines


class BoardState(GameEngines.Avalam.RawAvalamState):
    def __repr__(self):
        err = re.sub(r'(\d{2,}|[6-9])', fr'{Fore.LIGHTRED_EX}\1{Fore.RESET}', self.board.__str__())
        neg = re.sub(r'(-[1-5])', fr'{Fore.LIGHTBLUE_EX}\1{Fore.RESET}', err)
        pos = re.sub(r'((?: | \[)[1-5])', fr'{Fore.LIGHTYELLOW_EX}\1{Fore.RESET}', neg)
        return pos