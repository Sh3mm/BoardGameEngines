from pathlib import Path
import json
import numpy as np
from typing import Union
from GameEngines.UltiTTT import BoardState
from GameEngines.UltiTTT.PythonEngine import BoardState as PyBoardState


def load_state(file: Union[str, Path], *, py_engine=False) -> BoardState:
    data = json.loads(Path(file).read_text())

    state = PyBoardState if py_engine else BoardState

    data["board"] = np.array(data["board"]).reshape((9, 9))

    return state._load_data(data)


def save_state(file: Union[str, Path], state: BoardState):
    data = {
        "board": state.board.flatten().tolist(),
        "win_state": state._win_state,
        "active_cell": int(state._active_cell),
        "turn": state.turn,
        "active_pid": int(state.curr_pid)
    }
    Path(file).write_text(json.dumps(data))


""" File template
{
    board: [int],       // Flattened board from (9,9) to (81,)
    win_state: [int],   // The move cache from self._cached_moves
    active_cell: int,   // The current active cell of the meta-board
    turn: int,          // The current turn
    active_pid: int     // The active player 
}
"""