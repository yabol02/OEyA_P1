import itertools

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from .match import Match
from .player import Player


class Tournament:
    def __init__(
        self,
        players: tuple[Player, ...],
        stop_prob: float = 0.0,
        max_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 1,
    ):
        """
        Represents an all-against-all tournament among a group of players.

        :param players: Tuple of players that will participate in the tournament.
        :type players: tuple[Player, ...]
        :param stop_prob: Probability of stopping the match after each round in the match.
        :type stop_prob: float
        :param max_rounds: Maximum number of rounds in each match.
        :type max_rounds: int
        :param error: Probability of making an error (from 0 to 1).
        :type error: float
        :param repetitions: Number of matches each player plays against each other player.
        :type repetitions: int
        """
        self.players = players
        self.stop_prob = stop_prob
        self.max_rounds = max_rounds
        self.error = error
        self.repetitions = repetitions

        # This dictionary stores the ongoing ranking of the tournament.
        # Keys are Player instances and values are their accumulated points.
        self.ranking = {player: 0.0 for player in self.players}  # initial values

    def sort_ranking(self, print_ranking: bool = True) -> None:
        """
        Sorts the tournament ranking by score in descending order.

        This method reorders the ranking according to the points obtained by each player
        throughout the tournament, storing the result in a sorted list.

        :return: None
        :rtype: None
        """
        self.ranking = dict(
            sorted(self.ranking.items(), key=lambda item: item[1], reverse=True)
        )

        if print_ranking:
            tqdm.write("-" * 30)
            tqdm.write("FINAL RANKING")
            tqdm.write("-" * 30)
            for rank, (player, score) in enumerate(self.ranking.items(), 1):
                tqdm.write(f"#{rank}. {player.name.ljust(15)} | Score: {score:.2f}")
            tqdm.write("-" * 30)
        self.__ranking_sorted = True

    def play(self, print_step=False, ext_progress: bool = False) -> None:
        """
        Simulates the full tournament.

        This method simulates all matches among the players using an all-against-all structure.
        It updates the `self.ranking` dictionary with the total points accumulated by each player.

        :param print_step: If True, prints details of each match as it is played.
        :type print_step: bool
        :param ext_progress: Optional dictionary to configure an external progress bar.
        :type ext_progress: dict | None
        :return: None
        :rtype: None
        """
        self.ranking = {player: 0.0 for player in self.players}

        pairs = list(itertools.combinations(self.players, 2))
        total_matches = len(pairs)

        for player_1, player_2 in tqdm(
            iterable=pairs,
            desc="Tournament progress",
            total=total_matches,
            leave=False if ext_progress else True,
            position=1 if ext_progress else 0,
        ):
            for r in range(self.repetitions):
                match = Match(
                    player_1=player_1,
                    player_2=player_2,
                    stop_prob=self.stop_prob,
                    max_rounds=self.max_rounds,
                    error=self.error,
                )
                match.play(do_print=print_step)
                score_p1, score_p2 = match.score

                self.ranking[player_1] += score_p1
                self.ranking[player_2] += score_p2

                player_1.clean_history()
                player_2.clean_history()

    def play_trace(self, ext_progress: bool = False) -> pd.DataFrame:
        """
        Plays the tournament while extracting all the information from each match.


        :return: A Dataframe with all the games.
        :rtype: pd.DataFrame
        """
        all_match_results = []
        game_number = 1
        self.ranking = {player: 0.0 for player in self.players}

        pairs = list(itertools.combinations(self.players, 2))
        total_matches = len(pairs)

        for player_1, player_2 in tqdm(
            iterable=pairs,
            desc="Tournament progress",
            total=total_matches,
            leave=False if ext_progress else True,
            position=1 if ext_progress else 0,
        ):
            for r in range(self.repetitions):
                match = Match(
                    player_1=player_1,
                    player_2=player_2,
                    stop_prob=self.stop_prob,
                    max_rounds=self.max_rounds,
                    error=self.error,
                )

                match_results = match.play_trace()
                all_match_results.append(
                    {
                        "game_number": game_number,
                        "repetition": r + 1,
                        "num_rounds": match_results["rounds"],
                        "p1_name": match_results["p1_name"],
                        "p2_name": match_results["p2_name"],
                        "p1_action": match_results["p1_actions"],
                        "p2_action": match_results["p2_actions"],
                        "p1_payoff": match_results["p1_payoffs"],
                        "p2_payoff": match_results["p2_payoffs"],
                        "mean_score_p1": match_results["mean_score_p1"],
                        "mean_score_p2": match_results["mean_score_p2"],
                    }
                )

                score_p1, score_p2 = match.score
                self.ranking[player_1] += score_p1
                self.ranking[player_2] += score_p2

                player_1.clean_history()
                player_2.clean_history()
                game_number += 1

        return pd.DataFrame(all_match_results)

    def plot_results(self) -> None:
        """
        Plots a bar chart representing the final ranking.

        The x-axis should display the player names (sorted by their final score),
        and the y-axis should display the total points obtained by each player.

        :return: None
        :rtype: None
        """
        if not hasattr(self, "__ranking_sorted") or not self.__ranking_sorted:
            self.sort_ranking()

        names, scores = map(
            list, zip(*[(player.name, score) for player, score in self.ranking.items()])
        )

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

    def __repr__(self) -> str:
        return (
            f"Tournament(players_count={len(self.players)!r}, "
            f"max_rounds={self.max_rounds!r}, stop_prob={self.stop_prob!r}, "
            f"error={self.error!r}, repetitions={self.repetitions!r})"
        )

    def __str__(self) -> str:
        ranking_status = "PENDING"
        if any(score > 0.0 for score in self.ranking.values()):
            ranking_status = f"FINAL RANKING"

        return f"All-Against-All Tournament: {len(self.players)} players ({ranking_status})."
