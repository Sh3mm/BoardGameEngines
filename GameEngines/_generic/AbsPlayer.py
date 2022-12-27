from abc import ABC, abstractmethod
from GameEngines._generic import AbsBoardState


class AbsPlayer(ABC):
    @abstractmethod
    def play(self, board: AbsBoardState, moves: set, pid: int):
        ...

    def get_name(self) -> str:
        return 'Unnamed'
