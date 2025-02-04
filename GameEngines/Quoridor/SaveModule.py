from pathlib import Path
import json
import numpy as np
from typing import Union, Type, Dict, Any
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines import cache_utils
from GameEngines.Quoridor.utilsTypes import to_move


class QuoridorSave(AbsSaveModule):
    """ Json File Template
    {
        walls: [[int, int]],  // wall positions
        players: [[int, int]],// the player infos (position & walls left)
        turn: int,            // The current turn
        curr_pid: int         // The active player
    }
    """
    @staticmethod
    def load_state(file: Union[str, Path], state_type: Type[AbsBoardState]) -> AbsBoardState:
        data = json.loads(Path(file).read_text())

        data["walls"] = set((tuple(w[0]), tuple(w[1])) for w in data["walls"])
        data["board"] = None # todo
        return QuoridorSave._put_data(data, state_type)

    @staticmethod
    def save_state(file: Union[str, Path], state: AbsBoardState):
        data = QuoridorSave._get_data(state)
        Path(file).write_text(json.dumps(data))

    @staticmethod
    @cache_utils.get_cache
    def _get_data(state: AbsBoardState) -> Dict[str, Any]:
        return {
            "walls": state._walls,
            "players": state._players,
            "turn": state._turn,
            "curr_pid": state._curr_pid,
        }

    @staticmethod
    @cache_utils.put_cache(to_move)
    def _put_data(data: Dict[str, Any], state_type: Type[AbsBoardState]) -> AbsBoardState:
        state = state_type()

        state._board = data["board"]
        state._walls = data["walls"]
        state._players = data["players"]
        state._turn = data["turn"]
        state._curr_pid = data["curr_pid"]

        return state