from typing import Tuple, List, Dict
from avalamEngine import Game
from itertools import product
from avalamEngine.Players import Player, MiniMaxPlayer
from avalamEngine.heuristics.Heuristics import ratio_diff, board_pawn_diff, sure_ratio_dif
from avalamEngine.heuristics.DepthCalculators import exp_increase_float, exp_increase_int


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


if __name__ == '__main__':
    player_base = MiniMaxPlayer
    depth_f = [exp_increase_float, 3, 3.5]
    heuristic_f = [ratio_diff, board_pawn_diff, sure_ratio_dif]

    players = [
        MiniMaxPlayer(max_depth=df, heuristic=hf, p_name=f'{MiniMaxPlayer}|{df}|{hf}')
        for df, hf in product(depth_f, heuristic_f)
    ]
    Arena.round_robin(players, True)
