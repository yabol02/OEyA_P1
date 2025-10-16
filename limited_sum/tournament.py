from .player import Player


class Tournament:

    # Este método ya está implementado
    def __init__(
        self,
        players: tuple[Player, ...],
        n_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 2,
    ):
        """
        All-against-all tournament

        Parameters:
            - players (tuple[Player, ...]): tuple of players that will play the
         tournament
            - n_rounds (int = 100): number of rounds in each match
            - error (float = 0.0): error probability (in base 1)
            - repetitions (int = 2): number of matches each player plays against
         each other player
        """

        self.players = players
        self.n_rounds = n_rounds
        self.error = error
        self.repetitions = repetitions

        # This is a key variable of the class. It is intended to store the
        # ongoing ranking of the tournament. It is a dictionary whose keys are
        # the players in the tournament, and its corresponding values are the
        # points obtained in their interactions with each other. In the end, to
        # see the winner, it will be enough to sort this dictionary by the
        # values.
        self.ranking = {player: 0.0 for player in self.players}  # initial vals

    def sort_ranking(self) -> None:
        """Sort the ranking by the value (score)"""
        raise NotImplementedError

    # pista: utiliza 'itertools.combinations' para hacer los cruces
    def play(self) -> None:
        """
        Main call of the class. It must simulate the championship and update
        the variable 'self.ranking' with the accumulated points obtained by
        each player in their interactions.
        """
        raise NotImplementedError

    def plot_results(self):
        """
        Plots a bar chart of the final ranking. On the x-axis should appear
        the names of the sorted ranking of players participating in the
        tournament. On the y-axis the points obtained.
        """
        raise NotImplementedError
