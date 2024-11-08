from pathlib import Path
import json
import numpy as np
from typing import Union, Type, Dict, Any
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines import cache_utils
from GameEngines.UltiTTT.utilsTypes import to_move


class UltiTTTSave(AbsSaveModule):
    """ Json File Template
    {
        board: [int],       // Flattened board from (9,9) to (81,)
        win_state: [int],   // The move cache from self._cached_moves
        active_cell: int,   // The current active cell of the meta-board
        turn: int,          // The current turn
        curr_pid: int       // The active player
    }
    """
    @staticmethod
    def load_state(file: Union[str, Path], state_type: Type[AbsBoardState]) -> AbsBoardState:
        data = json.loads(Path(file).read_text())

        data["board"] = np.array(data["board"]).reshape((9, 9))

        return UltiTTTSave._put_data(data, state_type)

    @staticmethod
    def save_state(file: Union[str, Path], state: AbsBoardState):
        data = UltiTTTSave._get_data(state)
        Path(file).write_text(json.dumps(data))

    @staticmethod
    @cache_utils.get_cache
    def _get_data(state: AbsBoardState) -> Dict[str, Any]:
        return {
            "board": state.board.flatten().tolist(),
            "win_state": state._win_state,
            "active_cell": int(state._active_cell),
            "turn": state.turn,
            "curr_pid": int(state.curr_pid)
        }

    @staticmethod
    @cache_utils.put_cache(to_move)
    def _put_data(data: Dict[str, Any], state_type: Type[AbsBoardState]) -> AbsBoardState:
        state = state_type()

        state._board = data["board"]
        state._win_state = data["win_state"]
        state._active_cell = data["active_cell"]
        state._turn = data["turn"]
        state._curr_pid = data["curr_pid"]

        return state
