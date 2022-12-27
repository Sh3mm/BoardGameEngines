from abc import ABC, abstractmethod


class AbsBoardState(ABC):
    @property
    @abstractmethod
    def turn(self):
        ...

    @property
    @abstractmethod
    def board(self):
        ...

    @abstractmethod
    def play(self, move, pid: int) -> 'AbsBoardState':
        ...

    @abstractmethod
    def copy(self) -> 'AbsBoardState':
        ...

    @abstractmethod
    def get_legal_moves(self) -> list:
        ...

    @abstractmethod
    def winner(self) -> int:
        ...

    @abstractmethod
    def score(self) -> tuple:
        ...
