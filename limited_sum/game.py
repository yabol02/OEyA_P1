import numpy as np
from abc import ABC, abstractmethod
from typing import Sequence

ACTIONS = (0, 1, 2, 3, 4, 5)  # Acciones del juego de suma limitada
THRESHOLD = 5  # Umbral de suma


class Game:
    def __init__(self, actions: Sequence[int] = ACTIONS, threshold: int = THRESHOLD):
        """
        Represents the limited-sum game.

        :param actions: List of possible actions.
        :type actions: Sequence[int]
        :param threshold: Sum threshold beyond which both players get 0.
        :type threshold: int
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def payoff_matrix(self) -> np.ndarray:
        """
        Payoff matrix of the game.

        :return: The 6x6 payoff matrix.
        :rtype: numpy.ndarray
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate_result(self, a_1: int, a_2: int) -> tuple[float, float]:
        """
        Given two actions, returns the payoffs of both players.

        :param a_1: Action of player 1 (0 to 5).
        :type a_1: int
        :param a_2: Action of player 2 (0 to 5).
        :type a_2: int
        :return: Tuple containing the payoffs of player 1 and player 2, respectively.
        :rtype: tuple[float, float]
        """
        raise NotImplementedError
