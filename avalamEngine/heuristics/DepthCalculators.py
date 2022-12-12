from typing import Union
from avalamEngine import BoardState


def exp_increase_int(state: BoardState) -> int:
    max_move = len(state.base_board.base_moves)
    move_nb = len(state.get_legal_moves())

    x = max_move - move_nb
    return int(876 / (438 - x))


def exp_increase_float(state: BoardState) -> float:
    max_move = len(state.base_board.base_moves)
    move_nb = len(state.get_legal_moves())

    x = max_move - move_nb
    return 876 / (438 - x)


def find_num_states_to_explore(time_eslaped: float, time_allowed: int, tot_states_explored: int, turn: int) -> int:
    exploring_rate = tot_states_explored / max(time_eslaped, 1)
    num_turns_left = (35 - turn) / 2
    num_states_to_explore = (time_allowed - time_eslaped) * exploring_rate / max(num_turns_left, 1)
    return num_states_to_explore


def constant_states(turn: int, max_stats_to_explore) -> int:

    if turn <= 6:
        depth = 2
        return depth

    states_to_explore = 1
    initial_branching_factor = 48
    depth = 0

    while states_to_explore < max_stats_to_explore:
        depth += 1
        states_to_explore *= (initial_branching_factor - turn - depth)
    depth = min(10, max(1, depth))
    return depth
