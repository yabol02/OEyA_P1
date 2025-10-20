import itertools
import matplotlib.pyplot as plt
from .match import Match
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

        This method reorders the ranking according to the points obtained by each player
        throughout the tournament, storing the result in a sorted list.

        :return: None
        :rtype: None
        """
        sorted_items = sorted(
            self.ranking.items(), key=lambda item: item[1], reverse=True
        )

        self._sorted_ranking_list = sorted_items

        print("-" * 30)
        print("FINAL RANKING")
        print("-" * 30)
        for rank, (player, score) in enumerate(self._sorted_ranking_list, 1):
            print(f"#{rank}. {player.name.ljust(15)} | Score: {score:.2f}")

    def play(self) -> None:
        """
        Simulates the full tournament.

        This method simulates all matches among the players using an all-against-all structure.
        It updates the ``self.ranking`` dictionary with the total points accumulated by each player.

        :return: None
        :rtype: None
        """
        self.ranking = {player: 0.0 for player in self.players}

        for player_1, player_2 in itertools.combinations(self.players, 2):
            for _ in range(self.repetitions):
                match = Match(
                    player_1=player_1,
                    player_2=player_2,
                    n_rounds=self.n_rounds,
                    error=self.error,
                )
                match.play(do_print=False)
                score_p1, score_p2 = match.score

                self.ranking[player_1] += score_p1
                self.ranking[player_2] += score_p2

                player_1.clean_history()
                player_2.clean_history()

        print(
            f"Tournament finished with {len(self.players)} players, {self.n_rounds} rounds\, \
              and {self.repetitions} repetitions per pair."
        )

    def plot_results(self) -> None:
        """
        Plots a bar chart representing the final ranking.

        The x-axis should display the player names (sorted by their final score),
        and the y-axis should display the total points obtained by each player.

        :return: None
        :rtype: None
        """
        if not hasattr(self, "_sorted_ranking_list"):
            self.sort_ranking()

        names = [player.name for player, s in self._sorted_ranking_list]
        scores = [score for p, score in self._sorted_ranking_list]

        plt.figure(figsize=(10, 6))
        plt.bar(names, scores, color="skyblue")

        plt.xlabel("Estrategia del Jugador")
        plt.ylabel("Puntuación Total Acumulada")
        plt.title(
            f"Resultado del Torneo (Rondas: {self.n_rounds}, Reps: {self.repetitions})"
        )
        plt.xticks(rotation=45, ha="right")

        for i, score in enumerate(scores):
            plt.text(
                i, score + max(scores) * 0.01, f"{score:.2f}", ha="center", va="bottom"
            )

        plt.tight_layout()
        plt.show()
