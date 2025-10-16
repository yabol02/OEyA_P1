from .player import Player


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

        self.player_1 = player_1
        self.player_2 = player_2
        self.n_rounds = n_rounds
        self.error = error

        # This variable stores the final result of the match once 'play()' is called.
        # The tuple contains the points obtained by the first and second player,
        # respectively.
        self.score = (0.0, 0.0)

    def play(self, do_print: bool = False) -> None:
        """
        Plays the match between both players.

        This method executes all rounds of the match, updates the internal
        state, and stores the final result in ``self.score``.

        :param do_print: If True, prints the intermediate results after each round,
            including the round number, the last actions of both players, and the
            ongoing score.
        :type do_print: bool
        :return: None
        :rtype: None
        """
        raise NotImplementedError
