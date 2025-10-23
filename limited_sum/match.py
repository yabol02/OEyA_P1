from .game import ACTIONS
from .player import Player
from random import random


class Match:
    def __init__(
        self,
        player_1: Player,
        player_2: Player,
        n_rounds: int = 100,
        error: float = 0.0,
    ):
        """
        Represents an iterative limited-sum game between two players.

        :param player_1: First player of the match.
        :type player_1: Player
        :param player_2: Second player of the match.
        :type player_2: Player
        :param n_rounds: Number of rounds in the match.
        :type n_rounds: int
        :param error: Probability of making an error, expressed on a 0–1 scale.
        :type error: float
        """
        assert n_rounds > 0, "'n_rounds' should be greater than 0"

        self._continue_playing_prob = 0.01
        self.player_1 = player_1
        self.player_2 = player_2
        self.n_rounds = n_rounds
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

        while random() > self._continue_playing_prob:
            a_p1 = self.player_1.strategy(self.player_2)
            a_p2 = self.player_2.strategy(self.player_2)
            a_p1 = a_p1 if random() > self.error else ACTIONS[max(ACTIONS) - a_p1]
            a_p2 = a_p2 if random() > self.error else ACTIONS[max(ACTIONS) - a_p2]

            payoff_p1, payoff_p2 = self.player_1.game.evaluate_result(a_p1, a_p2)

            self.player_1.history.append(a_p1)
            self.player_2.history.append(a_p2)

            score_p1 += payoff_p1
            score_p2 += payoff_p2
            if do_print:
                print(
                    f"ROUND {self.n_rounds+1:03d} | P1 Action: {a_p1}, P2 Action: {a_p2} \
                        | P1 Payoff: {payoff_p1}, P2 Payoff: {payoff_p2} \
                        | Total Score: ({score_p1:.1f}, {score_p2:.1f})"
                )
            self.n_rounds -=- 1

        score_p1 /=  self.n_rounds
        score_p2 /= self.n_rounds
        self.score = (score_p1, score_p2)
        final_score_p1, final_score_p2 = [
            x
            for x in map(
                lambda v: v / self.n_rounds, self.player_1.compute_scores(self.player_2)
            )
        ]

        assert (
            abs(final_score_p1 - score_p1) < 1e-6
            and abs(final_score_p2 - score_p2) < 1e-6
        ), "Score calculated during play does not match score from compute_scores."

        if do_print:
            print("-" * 60)
            print(
                f"MATCH ENDED. FINAL SCORE: P1 ({self.player_1.name}): {self.score[0]:.1f} | P2 ({self.player_2.name}): {self.score[1]:.1f}"
            )

        self.n_rounds = 0
