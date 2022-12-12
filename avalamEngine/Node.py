from avalamEngine import BoardState, Move
from typing import Set


class Node:
    def __init__(
            self,
            board: BoardState,
            move: Move or None,
            level: int,
            max_level: int,
            parent: None or 'Node'
    ):
        """
        :param board: Board state of the current node
        :param move: The move needed to the board, from the previous board state (the parent's board)
        :param level: depth of the node in the tree. Root node has Depth = 0
        :param max_level: The max depth of the tree
        :param parent: The parent node. Is None if node is root and has no parent
        """
        self.board = board
        self.move = move
        self.level = level
        self.max_level = max_level
        self.parent = parent

        self.children: Set['Node'] = set()

    def __repr__(self):
        representation = \
            f'alpha: \t {self.alpha} \n' \
            f'beta:  \t {self.beta}  \n' \
            f'level: \t {self.level} \n'
        print(representation)

    def print_tree(self):
        print(self)
        for child in self.children:
            print(child)

    def generate_children(self):
        child_level = self.level + 1
        for move in self.board.moves:
            origin = move[0]
            dest = move[1]
            child_board = self.board.stack(origin, dest)
            child = Node(child_board, move, child_level, self.max_level, self)
            self.children.add(child)

    def generate_child(self, move: Move) -> 'Node':
        child_level = self.level + 1
        origin = move[0]
        dest = move[1]
        child_board = self.board.stack(origin, dest)
        child = Node(child_board, move, child_level, self.max_level, self)
        self.children.add(child)
        return child

    def is_terminal(self):
        return self.level >= self.max_level
