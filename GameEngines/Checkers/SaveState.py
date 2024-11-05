from pathlib import Path
import json
import numpy as np
from typing import Union
from GameEngines.Checkers import BoardState
from GameEngines.Checkers.PythonEngine import BoardState as PyBoardState


def load_state(file: Union[str, Path], *, py_engine=False) -> BoardState:
    data = json.loads(Path(file).read_text())

    state = PyBoardState if py_engine else BoardState

    data["board"] = np.array(data["board"]).reshape((7, 8))
    if data["cached_moves"] is not None:
        data["cached_moves"] = set((tuple(i[0]), tuple(i[1])) for i in data["cached_moves"])

    return state._load_data(data)


def save_state(file: Union[str, Path], state: BoardState):
    moves = state._cached_moves
    data = {
        "board": state.board.flatten().tolist(),
        "cached_moves": None if moves is None else list(moves),
        "turn": state.turn,
        "active_pid": state.curr_pid
    }
    Path(file).write_text(json.dumps(data))


""" File template
{
    board: [int],       // Flattened board from (9,9) to (81,)
    move_cache: [Move], // The move cache from self._cached_moves
    turn: int,          // The current turn
    active_pid: int     // The active player 
}
"""