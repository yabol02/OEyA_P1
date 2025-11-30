import itertools

import matplotlib.pyplot as plt
import pandas as pd

from .match import Match
from .player import Player


class Tournament:
    def __init__(
        self,
        players: tuple[Player, ...],
        prob_stop: float = 0.0,
        max_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 1,
    ):
        """
        Represents an all-against-all tournament among a group of players.

        :param players: Tuple of players that will participate in the tournament.
        :type players: tuple[Player, ...]
        :param prob_stop: Probability of stopping the match after each round in the match.
        :type prob_stop: float
        :param max_rounds: Maximum number of rounds in each match.
        :type max_rounds: int
        :param error: Probability of making an error (from 0 to 1).
        :type error: float
        :param repetitions: Number of matches each player plays against each other player.
        :type repetitions: int
        """
        self.players = players
        self.prob_stop = prob_stop
        self.max_rounds = max_rounds
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

    def play(self, print_step=False) -> None:
        """
        Simulates the full tournament.

        This method simulates all matches among the players using an all-against-all structure.
        It updates the `self.ranking` dictionary with the total points accumulated by each player.

        :return: None
        :rtype: None
        """
        self.ranking = {player: 0.0 for player in self.players}

        for player_1, player_2 in itertools.combinations(self.players, 2):
            for r in range(self.repetitions):
                match = Match(
                    player_1=player_1,
                    player_2=player_2,
                    prob_stop=self.prob_stop,
                    max_rounds=self.max_rounds,
                    error=self.error,
                )
                match.play(do_print=print_step)
                score_p1, score_p2 = match.score

                self.ranking[player_1] += score_p1
                self.ranking[player_2] += score_p2

                player_1.clean_history()
                player_2.clean_history()

        print(f"Tournament finished with {len(self.players)} players and {self.repetitions} repetitions per pair.")
    
    def play_trace(self) -> pd.DataFrame:
        """
        Plays the tournament while extracting all the information from each match.
        
        
        :return: A Dataframe with all the games.
        :rtype: pd.DataFrame
        """
        game_number = 1
        all_match_results = []
        self.ranking = {player: 0.0 for player in self.players}

        for player_1, player_2 in itertools.combinations(self.players, 2):
            for r in range(self.repetitions):
                match = Match(
                    player_1=player_1,
                    player_2=player_2,
                    prob_stop=self.prob_stop,
                    max_rounds=self.max_rounds,
                    error=self.error,
                )
                match_result =  match.play_trace()
                match_result["game_number"] = game_number
                match_result["repetition"] = r + 1
                all_match_results.append(match_result)

                score_p1, score_p2 = match.score
                self.ranking[player_1] += score_p1
                self.ranking[player_2] += score_p2

                player_1.clean_history()
                player_2.clean_history()
                game_number += 1

        print(f"Tournament finished with {len(self.players)} players and {self.repetitions} repetitions per pair.")
        return pd.DataFrame(all_match_results)

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
            f"Resultado del Torneo (Rondas: {self.max_rounds}, Reps: {self.repetitions})"
        )
        plt.xticks(rotation=45, ha="right")

        for i, score in enumerate(scores):
            plt.text(
                i, score + max(scores) * 0.01, f"{score:.2f}", ha="center", va="bottom"
            )

        plt.tight_layout()
        plt.show()
