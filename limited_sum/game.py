import numpy as np
from abc import ABC, abstractmethod
from typing import Sequence

ACTIONS = (0, 1, 2, 3, 4, 5)  # Acciones del juego de suma limitada
THRESHOLD = 5  # Umbral de suma



class Game:

    def __init__(self, actions: Sequence[int] = ACTIONS, threshold: int = THRESHOLD):
        """
        Represents the limited-sum game.

        Parameters:
            - actions (list[int]): list of possible actions (default: [0,1,2,3,4,5])
            - threshold (int): sum threshold beyond which both get 0 (default: 5)
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def payoff_matrix(self) -> np.ndarray:
        """
        Payoff matrix of the game.

        Returns:
            - 6x6 np array of the matrix
        """
        raise NotImplementedError


    @abstractmethod
    def evaluate_result(self, a_1: int, a_2: int) -> tuple[float, float]:
        """
        Given two actions, returns the payoffs of the two players.

        Parameters:
            - a_1 (int): action of player 1 (0 to 5)
            - a_2 (int): action of player 2 (0 to 5)

        Returns:
            - tuple of two floats, being the first and second values the payoff
            for the first and second player, respectively.
        """
        raise NotImplementedError
