import time
from math import inf
from random import random
from colorama import Fore
from GameEngines import AbsPlayer
from GameEngines.Avalam import BoardState, Move
from typing import Set, List, Tuple, Union
from Players.Avalam.minimax_utils import Heuristic, DepthCalculator


class MiniMaxPlayer(AbsPlayer):
    ENDING_SCORE = 1000  # usage : score in a final state

    def __init__(self, max_depth: Union[float, DepthCalculator], heuristic: Heuristic, p_name: str = None):
        self.name = p_name
        self.max_depth = max_depth
        self.heuristic = heuristic
        self.total_time = 0

    def play(self, board: BoardState, moves: Set[Move], pid: int) -> Move:
        start_time = time.time()
        if isinstance(self.max_depth, (float, int)):
            max_depth = self.max_depth
        else:
            max_depth = self.max_depth(board)

        value, best_actions = self.minimax_search(board, 0, pid, max_depth)
        total_time = time.time() - start_time
        print(
            f'{Fore.LIGHTBLUE_EX if pid == 1 else Fore.LIGHTYELLOW_EX}'
            f'depth: {max_depth: 5.3f}'
            f'| score: {value: 5.3f}',
            f'| action: {best_actions[0]}',
            f'| time: {total_time}'
            f'{Fore.RESET}'
        )
        return best_actions[0]

    def minimax_search(
            self, state: BoardState, depth: int, pid: int, max_depth: Union[float, int],
            prev_actions: List[Move] = None, is_max=True, alpha=-inf, beta=inf, is_final=False
    ) -> Tuple[float, List[Move]]:
        if prev_actions is None:
            prev_actions = []

        # terminal state
        if not is_final and len(state.get_legal_moves()) == 0:
            return self.get_terminal_score(pid, prev_actions, state)

        # Max depth reached
        if max_depth - depth < random() or is_final:
            return self.heuristic(state, pid), prev_actions

        # Min max
        value = -inf if is_max else inf
        best_actions = None

        actions = state.get_legal_moves()
        for a in actions:
            next_steps = [*prev_actions, a]
            #print(next_steps)
            successor = state.play(*a)
            suc_is_final = len(actions) > 18 and max_depth - (depth + 1) < random()

            new_value, new_actions = self.minimax_search(
                successor, depth + 1, pid, max_depth, next_steps, not is_max, alpha, beta, suc_is_final
            )

            should_change = new_value > value if is_max else new_value < value
            if should_change:
                value = new_value
                best_actions = new_actions
                # max pruning
                if is_max:
                    alpha = max(alpha, value)
                    if value >= beta:
                        return value, best_actions
                # min pruning
                else:
                    beta = min(beta, value)
                    if value <= alpha:
                        return value, best_actions

        return value, best_actions

    def get_terminal_score(self, pid: int, prev_actions: List[Move], state: BoardState):
        count = state.count()
        if count[pid] > count[1 - pid]:
            return self.ENDING_SCORE, prev_actions
        else:
            return -self.ENDING_SCORE, prev_actions
