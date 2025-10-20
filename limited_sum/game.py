import numpy as np
from abc import abstractmethod
from typing import Sequence

ACTIONS = (0, 1, 2, 3, 4, 5)  # Actions of the limited sum game
THRESHOLD = 5  # Threshold of the game


class Game:
    def __init__(self, actions: Sequence[int] = ACTIONS, threshold: int = THRESHOLD):
        """
        Represents the limited-sum game.

        :param actions: List of possible actions.
        :type actions: Sequence[int]
        :param threshold: Sum threshold beyond which both players get 0.
        :type threshold: int
        """
        self.actions = actions
        self.threshold = threshold

    @property
    @abstractmethod
    def payoff_matrix(self) -> np.ndarray[np.uint8]:
        """
        Payoff matrix of the game.

        :return: The 6x6 payoff matrix.
        :rtype: numpy.ndarray[numpy.uint8]
        """
        return np.array(
            [
                [(i, j) if i + j <= THRESHOLD else (0, 0) for j in ACTIONS]
                for i in ACTIONS
            ],
            dtype=np.uint8,
        )

    @abstractmethod
    def evaluate_result(self, a_1: int, a_2: int) -> tuple[float, float]:
        """
        Given two actions, returns the payoffs of both players.

        :param a_1: Action of player 1 (0 to 5).
        :type a_1: int
        :param a_2: Action of player 2 (0 to 5).
        :type a_2: int
        :return: Tuple containing the payoffs of player 1 and player 2, respectively.
        :rtype: tuple[int, int]
        """
        res_1, res_2 = self.payoff_matrix[a_1, a_2]
        return res_1, res_2
