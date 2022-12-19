from random import choice
from Players.Avalam.mcts_utils import Node, Simulator
from GameEngines.Avalam import BoardState


class MctsTree:
    def __init__(self, sim_func: Simulator, c=1.414):
        self.root = Node()
        self.root.gen_children()

        self.sim_func = sim_func
        self.c = c

    def simulate(self, sim_num: int):
        for i in range(sim_num):
            node = self._selection()
            node = self._expansion(node)
            result = self._simulation(node)
            self._back_prop(node, result)
        print()

    def _selection(self) -> Node:
        node = self.root
        while not node.is_terminal():
            node = max(node.children, key=lambda n: n.score(self.c))
        return node

    def _expansion(self, node: Node) -> Node:
        if node.sim_num == 0:
            return node
        node.gen_children()
        if node.is_terminal():
            return node
        return choice(node.children)

    def _simulation(self, node: Node) -> float:
        return self.sim_func(node.state)

    def _back_prop(self, node: Node, update: float):
        node.back_prop(update)


if __name__ == '__main__':
    def f(state: BoardState) -> float:
        pid = state.turn % 2
        self_keep, other_keep = (state.board > 0, state.board < 0) if pid == 0 else (state.board < 0, state.board > 0)
        self_ratio = state.board[self_keep] / state.ratios[pid, self_keep]
        other_ratio = state.board[other_keep] / state.ratios[1 - pid, other_keep]

        self_points = abs(self_ratio.sum())
        other_points = abs(other_ratio.sum())

        return int(self_points - other_points > 0)


    tree = MctsTree(f)
    tree.simulate(20000)
    print(sorted(tree.root.children, reverse=True, key=lambda n: n.tot_value / n.sim_num if n.sim_num != 0 else 0))
