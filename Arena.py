from typing import Tuple, List, Dict
from Avalam import Avalam, Player
from itertools import product


class Arena:
    @staticmethod
    def lineup(matches: List[Tuple[Player, Player]], both_side=False, show_results=False) -> List[tuple]:
        result = [Avalam(p0, p1).play(show_results) for p0, p1 in matches]
        if both_side:
            result += [Avalam(p1, p0).play(show_results) for p0, p1 in matches]

        return result

    @staticmethod
    def versus(match: Tuple[Player, Player], both_side=False, show_results=False) -> List[tuple]:
        result = [Avalam(match[0], match[1]).play(show_results)]
        if both_side:
            result = [result, Avalam(match[1], match[0]).play(show_results)]

        return result

    @staticmethod
    def round_robin(players: List[Player], show_results=False) -> Dict[str, tuple]:
        matches = product(players, players)
        result = {}
        for p0, p1 in matches:
            res = Avalam(p0, p1).play(show_results)
            result[f"{p0.name}-{p1.name}"] = res
            print(f'{p0.name}: {sum(res[2][1][::2])}\n{p1.name}: {sum(res[2][1][1::2])}\n')

        return result
