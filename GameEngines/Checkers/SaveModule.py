from pathlib import Path
import json
import numpy as np
from typing import Union, Type, Dict, Any
from GameEngines.abstract import AbsBoardState, AbsSaveModule
from GameEngines import cache_utils
from GameEngines.Checkers.utilsTypes import to_move


class CheckersSave(AbsSaveModule):
    """ Json File Template
    {
        board: [int],         // Flattened board from (9,9) to (81,)
        cached_moves: [Move], // The move cache from self._cached_moves
        turn: int,            // The current turn
        curr_pid: int         // The active player
    }
    """
    @staticmethod
    def load_state(file: Union[str, Path], state_type: Type[AbsBoardState]) -> AbsBoardState:
        data = json.loads(Path(file).read_text())

        data["board"] = np.array(data["board"]).reshape((7, 8))
        if data["cached_moves"] is not None:
            data["cached_moves"] = set((tuple(i[0]), tuple(i[1])) for i in data["cached_moves"])

        return CheckersSave._put_data(data, state_type)

    @staticmethod
    def save_state(file: Union[str, Path], state: AbsBoardState):
        data = CheckersSave._get_data(state)
        Path(file).write_text(json.dumps(data))

    @staticmethod
    @cache_utils.get_cache
    def _get_data(state: AbsBoardState) -> Dict[str, Any]:
        moves = state._cached_moves
        return {
            "board": state.board.flatten().tolist(),
            "cached_moves": None if moves is None else list(moves),
            "turn": int(state.turn),
            "curr_pid": int(state.curr_pid)
        }

    @staticmethod
    @cache_utils.put_cache(to_move)
    def _put_data(data: Dict[str, Any], state_type: Type[AbsBoardState]) -> AbsBoardState:
        state = state_type()

        state._board = data["board"]
        state._cached_moves = data["cached_moves"]
        state._turn = data["turn"]
        state._curr_pid = data["curr_pid"]

        return state
