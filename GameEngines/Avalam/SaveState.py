from pathlib import Path
import json
import numpy as np
from typing import Union
from GameEngines.Avalam import BoardState
from GameEngines.Avalam.PythonEngine import BoardState as PyBoardState


def load_state(file: Union[str, Path], *, py_engine=False) -> BoardState:
    data = json.loads(Path(file).read_text())

    state = PyBoardState if py_engine else BoardState

    data["board"] = np.array(data["board"]).reshape((9, 9))
    data["ratios"] = np.array(data["ratios"]).reshape((2, 9, 9))
    data["move_cache"] = set((tuple(i[0]), tuple(i[1])) for i in data["move_cache"])

    return state._load_data(data)


def save_state(file: Union[str, Path], state: BoardState):
    data = {
        "board": state.board.flatten().tolist(),
        "ratios": state.ratios.flatten().tolist(),
        "move_cache": list(state._moves),
        "on_move_call": state._on_move_call,
        "turn": state.turn,
        "active_pid": state.curr_pid
    }
    Path(file).write_text(json.dumps(data))


""" File template
{
    board: [int],       // Flattened board from (9,9) to (81,)
    ratios: [int]        / Flattened ratio board from (2, 9,9) to (162,)
    move_cache: [Move], // The move cache from self._moves
    on_move_call: Move, // The previous move cache from self._on_move_call
    turn: int,          // The current turn
    active_pid: int     // The active player 
}
"""