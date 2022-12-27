from typing import Set
from GameEngines import AbsPlayer
from GameEngines.Avalam import BoardState, Move
from Players.Avalam.mcts_utils import MctsTree, Simulator


class MctsPlayer(AbsPlayer):

    def __init__(self, sim_per_step, sim_func: Simulator):
        self.mcts = MctsTree(sim_func)
        self.sim_per_step = sim_per_step

    def play(self, board: BoardState, moves: Set[Move], pid: int) -> Move:
        self.mcts.update_tree(board)
        self.mcts.simulate(self.sim_per_step)
        return self.mcts.choose_and_update()
