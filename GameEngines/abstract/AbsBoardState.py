from typing import Type, Union
from abc import ABC, abstractmethod
import numpy as np
from pathlib import Path


class AbsBoardState(ABC):
    """
    This is the abstract implementation of any board state.
    It defines all necessary methods for a player to play a move
    """
    @abstractmethod
    def __init__(self, *, save_module: Type['AbsSaveModule'] = None): ...


    @abstractmethod
    def __eq__(self, other: 'AbsSaveModule') -> bool: ...

    @property
    @abstractmethod
    def turn(self) -> int:
        """
        getter for the current turn of a game according to the state

        :return: an int representing the current turn
        """
        ...

    @property
    @abstractmethod
    def curr_pid(self) -> int:
        """
        getter for the current player ID of a game according to the state

        :return: The current Player ID
        """
        ...

    @property
    @abstractmethod
    def board(self) -> np.ndarray:
        """
        getter for the raw form of the board in a numpy array

        :return: a ndarray the raw board
        """
        ...

    @abstractmethod
    def play(self, move) -> 'AbsBoardState':
        """
        method used to create the next state of the game if a move is played. The method does NOT verify that the move
        is legal and will play it regardless

        :param move: the move to be played
        :return: a new static BoardState
        """
        ...

    @abstractmethod
    def copy(self, *, cache=False) -> 'AbsBoardState':
        """
        method used to get a deep copy of the BoardState

        :param cache: if the cache state should be copied
        :return: a copy if the BoardState
        """
        ...

    @abstractmethod
    def get_legal_moves(self, *, cache=False) -> set:
        """
        method used to get all legal moves that can be executed at the current moment for the current player.
        :param cache:
        :return: a set of legal moves
        """
        ...

    @abstractmethod
    def winner(self) -> int:
        """
        method used to get the pid of the current winner of the game. \n
        If the game is unfinished, the method will return 0 \n
        If the game is a tie, it will return -1

        :return: -1, 0 or the winner's pid
        """
        ...

    @abstractmethod
    def score(self) -> tuple:
        """
        returns the current score of the game if it exists. If the game does not posses the concept of score before
        the end of the game, all players will be scored 0

        :return: a tuple of the current score of all players
        """
        ...

    @staticmethod
    @abstractmethod
    def load(file: Union[str, Path]) -> 'AbsBoardState':
        """
        Loads the board state from a file using the given SaveModule
        :param file: The str or path to the file
        :return: The loaded board state
        """
        ...

    @abstractmethod
    def save(self, file: Union[str, Path]):
        """
        Saves the board state in a file using the given SaveModule
        :param file: The str or path to the file
        """
        ...


class AbsSaveModule(ABC):
    """
    This is the abstract implementation of any state saving system.
    It defines all necessary methods to save and load data from a file
    """

    @staticmethod
    @abstractmethod
    def load_state(file: Union[str, Path], state_type: Type[AbsBoardState]) -> AbsBoardState:
        """
        this is the default method to load data from a file into a BoardState
        """
        ...

    @staticmethod
    @abstractmethod
    def save_state(file: Union[str, Path], state: AbsBoardState):
        """
        this is the default method to save data from a BoardState to a file.
        """
        ...