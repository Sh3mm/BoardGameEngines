from typing import Tuple, List, Dict
from Avalam import Game, Player
from itertools import product


class Arena:
    @staticmethod
    def lineup(matches: List[Tuple[Player, Player]], both_side=False, show_results=False) -> List[tuple]:
        result = [Game(p0, p1).play(show_results) for p0, p1 in matches]
        if both_side:
            result += [Game(p1, p0).play(show_results) for p0, p1 in matches]

        return result

    @staticmethod
    def versus(match: Tuple[Player, Player], both_side=False, show_results=False) -> List[tuple]:
        result = [Game(match[0], match[1]).play(show_results)]
        if both_side:
            result = [result, Game(match[1], match[0]).play(show_results)]

        return result

    @staticmethod
    def round_robin(players: List[Player], show_results=False) -> Dict[str, tuple]:
        matches = product(players, players)
        result = {}
        for p0, p1 in matches:
            res = Game(p0, p1).play(show_results)
            result[f"{p0.name}-{p1.name}"] = res
            print(f'{p0.name}: {sum(res[2][1][::2])}\n{p1.name}: {sum(res[2][1][1::2])}\n')

        return result
