from pathlib import Path
import json
import numpy as np
from typing import Union, Type, Any, Dict
from GameEngines.abstract import AbsSaveModule, AbsBoardState
from GameEngines import cache_utils
from GameEngines.Avalam.utilsTypes import to_move


class AvalamSave(AbsSaveModule):
    """ Json File Template
    {
        board: [int],       // Flattened board from (9,9) to (81,)
        ratios: [int]        / Flattened ratio board from (2, 9,9) to (162,)
        turn: int,          // The current turn
        curr_pid: int     // The active player
    }
    """

    @staticmethod
    def load_state(file: Union[str, Path], state_type: Type[AbsBoardState]) -> AbsBoardState:
        data = json.loads(Path(file).read_text())

        data["board"] = np.array(data["board"]).reshape((9, 9))
        data["ratios"] = np.array(data["ratios"]).reshape((2, 9, 9))

        return AvalamSave._put_data(data, state_type)

    @staticmethod
    def save_state(file: Union[str, Path], state: AbsBoardState):
        data = AvalamSave._get_data(state)
        Path(file).write_text(json.dumps(data))

    @staticmethod
    @cache_utils.get_cache
    def _get_data(state: AbsBoardState) -> Dict[str, Any]:
        return {
            "board": state.board.flatten().tolist(),
            "ratios": state.ratios.flatten().tolist(),
            "turn": state.turn,
            "curr_pid": state.curr_pid
        }

    @staticmethod
    @cache_utils.put_cache(to_move)
    def _put_data(data: Dict[str, Any], state_type: Type[AbsBoardState]) -> AbsBoardState:
        state = state_type()

        state._board = data["board"]
        state._ratios = data["ratios"]
        state._turn = data["turn"]
        state._curr_pid = data["curr_pid"]

        return state