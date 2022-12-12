import math
from avalamEngine.heuristics import Heuristic

from avalamEngine import Node, Move


def minimax_search(node: Node, heuristic: Heuristic) -> {int, Move or None}:
    alpha = -math.inf
    beta = math.inf

    def min_value(node: Node, alpha: int, beta: int) -> {int, Move or None}:
        best_move = None
        if node.is_terminal():
            score = heuristic(node.board, 0)  # todo: change to add player id since it wont work for other player
            return score, best_move

        for move in node.board.moves:
            child = node.generate_child(move)
            score, x = max_value(child, alpha, beta)
            if score < beta:
                beta = score
                best_move = move
            if beta <= alpha:
                break

        return beta, best_move

    def max_value(node: Node, alpha: int, beta: int) -> {int, Move or None}:
        best_move = None
        if node.is_terminal():
            score = heuristic(node.board, 0)  # todo: change to add player id since it wont work for other player
            return score, best_move

        for move in node.board.moves:
            child = node.generate_child(move)
            score, x = min_value(child, alpha, beta)
            if score > alpha:
                alpha = score
                best_move = move
            if beta <= alpha:
                break

        return alpha, best_move

    best_score, best_move = max_value(node, alpha, beta)



    return best_score, best_move






