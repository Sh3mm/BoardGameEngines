from GameEngines.Avalam import BoardState


def exp_increase_int(state: BoardState) -> int:
    max_move = len(BoardState.INIT_MOVES)
    move_nb = len(state.get_legal_moves(0))

    x = max_move - move_nb
    return int(876 / (438 - x))


def exp_increase_float(state: BoardState) -> float:
    max_move = len(BoardState.INIT_MOVES)
    move_nb = len(state.get_legal_moves(0))

    x = max_move - move_nb
    return 876 / (438 - x)
