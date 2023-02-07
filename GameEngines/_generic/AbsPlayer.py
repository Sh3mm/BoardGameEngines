from abc import ABC, abstractmethod
from GameEngines._generic import AbsBoardState
from typing import TypeVar, Set

T = TypeVar('T')


class AbsPlayer(ABC):
    @abstractmethod
    def play(self, board: AbsBoardState, moves: Set[T], pid: int) -> T:
        """
        method used to make a specified player chose a move between the option given

        :param board: the current BoardState
        :param moves: the set of allowed moves
        :param pid: the player ID the player will use
        :return: a move of the given list
        """
        ...

    @property
    def name(self) -> str:
        """
        getter for the name of a player. By default, the name is 'Unnamed'

        :return: a str of the player name
        """
        try:
            return self._name
        except AttributeError:
            return 'Unnamed'
