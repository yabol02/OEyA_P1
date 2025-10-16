from .player import Player


class Tournament:
    def __init__(
        self,
        players: tuple[Player, ...],
        n_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 2,
    ):
        """
        Represents an all-against-all tournament among a group of players.

        :param players: Tuple of players that will participate in the tournament.
        :type players: tuple[Player, ...]
        :param n_rounds: Number of rounds in each match.
        :type n_rounds: int
        :param error: Probability of making an error (from 0 to 1).
        :type error: float
        :param repetitions: Number of matches each player plays against each other player.
        :type repetitions: int
        """
        self.players = players
        self.n_rounds = n_rounds
        self.error = error
        self.repetitions = repetitions

        # This dictionary stores the ongoing ranking of the tournament.
        # Keys are Player instances and values are their accumulated points.
        self.ranking = {player: 0.0 for player in self.players}  # initial values

    def sort_ranking(self) -> None:
        """
        Sorts the tournament ranking by score in descending order.

        This method should reorder the ranking according to the points obtained
        by each player throughout the tournament.

        :return: None
        :rtype: None
        """
        raise NotImplementedError

    def play(self) -> None:
        """
        Simulates the full tournament.

        This method must simulate all matches among the players using
        an all-against-all structure. It updates the ``self.ranking``
        dictionary with the total points accumulated by each player.

        :return: None
        :rtype: None
        """
        raise NotImplementedError

    def plot_results(self) -> None:
        """
        Plots a bar chart representing the final ranking.

        The x-axis should display the player names (sorted by their final score),
        and the y-axis should display the total points obtained by each player.

        :return: None
        :rtype: None
        """
        raise NotImplementedError
