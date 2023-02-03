from GameEngines.Avalam import Move, BoardState
from typing import Union


class Node:
    def __init__(self, move: Move = None, parent: Union[None, 'Node'] = None):
        self.parent = parent
        self.move = move

        self.children = None
        self._end_state = None

        self._state = BoardState() if move is None else None

        self.tot_value = 0
        self.sim_num = 0

    def __repr__(self):
        return f"{self.tot_value} / {self.sim_num}"

    def is_terminal(self):
        if self.end_state:
            return True
        return self.sim_num == 0 or self.children is None

    def score(self, c=1.1414):
        if self.sim_num == 0:
            return 1

        if self.parent is None:
            return self.tot_value / self.sim_num

        return self.tot_value / self.sim_num + (c * self.parent.sim_num ** .5 / self.sim_num)

    def gen_children(self):
        if self.end_state:
            return

        self.children = [Node(move, self) for move in self.state.get_legal_moves(0)]

    def back_prop(self, result: float):
        self.tot_value += result
        self.sim_num += 1
        if self.parent is None:
            return

        self.parent.back_prop(-result)

    @property
    def end_state(self):
        if self._end_state is None:
            self._end_state = len(self.state.get_legal_moves(0)) == 0
        return self._end_state

    @property
    def state(self):
        if self._state is None:
            self._state = self.parent.state.play(*self.move)
        return self._state
