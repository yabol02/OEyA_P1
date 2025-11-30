from random import random

import pandas as pd

from .game import ACTIONS
from .player import Player


class Match:
    def __init__(
        self,
        player_1: Player,
        player_2: Player,
        prob_stop: float = 0.0,
        max_rounds: int = 100,
        error: float = 0.0,
    ):
        """
        Represents an iterative limited-sum game between two players.

        :param player_1: First player of the match.
        :type player_1: Player
        :param player_2: Second player of the match.
        :type player_2: Player
        :param prob_stop: Probability of stopping the match after each round.
        :type prob_stop: float
        :param max_rounds: Number of max rounds in the match.
        :type max_rounds: int
        :param error: Probability of making an error, expressed on a 0–1 scale.
        :type error: float
        """
        assert max_rounds > 0, "'max_rounds' should be greater than 0"

        self.prob_stop = prob_stop
        self.max_rounds = max_rounds
        self._round_counter = 1
        self.player_1 = player_1
        self.player_2 = player_2
        self.error = error

        self.player_1.clean_history()
        self.player_2.clean_history()

        # This variable stores the final result of the match once 'play()' is called.
        # The tuple contains the points obtained by the first and second player, respectively.
        self.score = (0.0, 0.0)

    def play(self, do_print: bool = False) -> None:
        """
        Plays the match between both players.

        This method executes all rounds of the match, updates the internal state, and stores the final
        result in ``self.score``.

        :param do_print: If True, prints the intermediate results after each round, including the round
                            number, the last actions of both players, and the ongoing score.
        :type do_print: bool
        :return: None
        :rtype: None
        """
        score_p1, score_p2 = 0, 0

        while (random() > self.prob_stop) and (self._round_counter < self.max_rounds):

            a_p1 = self.player_1.strategy(self.player_2)
            a_p2 = self.player_2.strategy(self.player_1)
            a_p1 = a_p1 if random() > self.error else ACTIONS[max(ACTIONS) - a_p1]
            a_p2 = a_p2 if random() > self.error else ACTIONS[max(ACTIONS) - a_p2]

            payoff_p1, payoff_p2 = self.player_1.game.evaluate_result(a_p1, a_p2)

            self.player_1.history.append(a_p1)
            self.player_2.history.append(a_p2)

            score_p1 += payoff_p1
            score_p2 += payoff_p2
            if do_print:
                print(
                    f"ROUND {self._round_counter:03d} | P1 Action: {a_p1}, P2 Action: {a_p2} \
                        | P1 Payoff: {payoff_p1}, P2 Payoff: {payoff_p2} \
                        | Total Score: ({score_p1:.1f}, {score_p2:.1f})"
                )
            self._round_counter += 1

        if self._round_counter == self.max_rounds:
            print("Maximum number of rounds reached.")

        score_p1 /= self._round_counter
        score_p2 /= self._round_counter
        self.score = (score_p1, score_p2)
        final_score_p1, final_score_p2 = [
            x
            for x in map(
                lambda v: v / self._round_counter,
                self.player_1.compute_scores(self.player_2),
            )
        ]

        assert (
            abs(final_score_p1 - score_p1) < 1e-6
            and abs(final_score_p2 - score_p2) < 1e-6
        ), "Score calculated during play does not match score from compute_scores."

        if do_print:
            print(
                f"MATCH ENDED. FINAL SCORE: P1 ({self.player_1.name}): {self.score[0]:.1f} | P2 ({self.player_2.name}): {self.score[1]:.1f}"
            )
            winner = (
                self.player_1.name
                if self.score[0] > self.score[1]
                else self.player_2.name
            )
            print(f"The winner is {winner}, with a score of {max(self.score):.1f}.")
            print("-" * 60)

    def play_trace(self) -> dict:
        """
        Plays the match between both players.

        This method executes all rounds of the match, updates the internal state, and stores the final
        result in ``self.score``.

        It also returns a Dict with the history of actions and payoffs for each round.

        :return: A dict containing the history of actions and payoffs for each round.
        :rtype: dict
        """
        score_p1, score_p2 = 0, 0

        player_1_payoffs = []
        player_2_payoffs = []

        while (random() > self.prob_stop) and (self._round_counter < self.max_rounds):

            a_p1 = self.player_1.strategy(self.player_2)
            a_p2 = self.player_2.strategy(self.player_1)
            a_p1 = a_p1 if random() > self.error else ACTIONS[max(ACTIONS) - a_p1]
            a_p2 = a_p2 if random() > self.error else ACTIONS[max(ACTIONS) - a_p2]

            payoff_p1, payoff_p2 = self.player_1.game.evaluate_result(a_p1, a_p2)

            player_1_payoffs.append(int(payoff_p1))
            player_2_payoffs.append(int(payoff_p2))

            self.player_1.history.append(a_p1)
            self.player_2.history.append(a_p2)

            score_p1 += payoff_p1
            score_p2 += payoff_p2

            self._round_counter += 1

        score_p1 /= self._round_counter
        score_p2 /= self._round_counter
        self.score = (score_p1, score_p2)
        final_score_p1, final_score_p2 = [
            x
            for x in map(
                lambda v: v / self._round_counter,
                self.player_1.compute_scores(self.player_2),
            )
        ]

        assert (
            abs(final_score_p1 - score_p1) < 1e-6
            and abs(final_score_p2 - score_p2) < 1e-6
        ), "Score calculated during play does not match score from compute_scores."

        data = {
            "rounds": self._round_counter,
            "p1_name": self.player_1.name,
            "p2_name": self.player_2.name,
            "p1_actions": self.player_1.history,
            "p2_actions": self.player_2.history,
            "p1_payoffs": player_1_payoffs,
            "p2_payoffs": player_2_payoffs,
            "mean_score_p1": float(final_score_p1),
            "mean_score_p2": float(final_score_p2),
        }

        return data
