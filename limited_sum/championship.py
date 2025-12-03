"""
Docstring for OEyA_P1.limited_sum.final_tournament

Class for playing the final tournament of the practice. This tournament will evaluate our players performance.

"""

import numpy as np
import pandas as pd

from limited_sum import tournament

from .game import Game
from .match import Match
from .player import Player
from .tournament import Tournament


class Championship:
    points_1st_phase = {1: 24, 2: 17, 3: 12, 4: 8, 5: 4, 6: 4}
    points_2nd_phase = {1: 24, 2: 17, 3: 12}
    points_3rd_phase = {1: 12, 2: 8, 3: 4}

    def __init__(
        self,
        players: tuple[Player, ...],
        # all_players: tuple[Player, ...],
        max_rounds: int = 400,
        stop_prob: float = 0.01,
        error: float = 0.01,
        repetitions: int = 2,
        representatives: int = 5,
    ):
        self.players = players
        assert len(players) == len(
            set(p.name for p in players)
        ), "Player names must be unique !!!"
        # self.all_players = all_players
        self.max_rounds = max_rounds
        self.stop_prob = stop_prob
        self.error = error
        self.repetitions = repetitions
        # self.points_table = {}
        self.ranking = {player.name: 0 for player in players}

    def play(self, do_print: bool = False):
        self._first_phase()
        if do_print:
            self._print_ranking("First Phase")

        self._second_phase()
        if do_print:
            self._print_ranking("Second Phase")

        self._third_phase()
        if do_print:
            self._print_ranking("Third Phase")

    def _update_ranking(self, results: pd.DataFrame, points_map: dict):
        """
        Updates the ranking based on the results of a tournament phase.

        :param results: DataFrame with 'player' and 'scores', sorted by average score.
        :type results: pd.DataFrame
        :param points_map: Dictionary of points by position (1, 2, 3, ...).
        :type points_map: dict
        """
        for rank, row in results.iterrows():
            self.ranking[row["player"].name] += points_map.get(rank + 1, 0)

    def _sort_results(self, results: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts the tournament results and computes the average score for each player.

        :param results: DataFrame containing the results of the tournament.
        :type results: pd.DataFrame
        :return: DataFrame with players and their average scores, sorted in descending order. Its columns are 'player' and 'scores'.
        :rtype: pd.DataFrame
        """
        punctuations = dict()
        for p in self.players:
            conditions = [
                (results["p1_name"] == p.name),
                (results["p2_name"] == p.name),
            ]
            choices = [results["mean_score_p1"], results["mean_score_p2"]]
            points = np.select(conditions, choices, default=np.nan)
            points = points[~np.isnan(points)]
            punctuations[p] = points.sum()
        punctuations = dict(
            sorted(punctuations.items(), key=lambda item: item[1], reverse=True)
        )
        return pd.DataFrame(punctuations.items(), columns=["player", "scores"])

    def _print_ranking(self, phase_name: str):
        """
        Prints the current ranking after a tournament phase. It shows the ranking sorted by total score (dictionary value) from highest to lowest.
        """
        print(f"\n{phase_name} completed. Current Ranking:")
        sorted_ranking = dict(
            sorted(self.ranking.items(), key=lambda item: item[1], reverse=True)
        )
        for player, points in sorted_ranking.items():
            print(f"  {player}: {points} points")
        print("-" * 30)

    def _first_phase(self):
        tournament = Tournament(
            players=self.players,
            stop_prob=self.stop_prob,
            max_rounds=self.max_rounds,
            error=self.error,
            repetitions=self.repetitions,
        )

        # Play tournament and process results
        res1 = tournament.play_trace()
        res1 = self._sort_results(res1)

        # Guardar datos de la evolución TODO: no entiendo qué queremos hacer aquí

        # Update ranking based on self.points_1st_phase
        self._update_ranking(res1, self.points_1st_phase)

    def _second_phase(self):
        points = {1: 24, 2: 17, 3: 12}  # maybe change it to a list
        # Pasar Match con personalizacione (400 rondas, 0.01 probabilidad de fin)
        # Instaciar nueva evolution con los jugadores "buenos"

        # Calcular puntuaciones y actualizar ranking
        raise NotImplementedError("Still not implemented")

    def _third_phase(self):
        points = {1: 12, 2: 8, 3: 4}  # maybe change it to a list
        # Pasar Match con personalizacione (400 rondas, 0.01 probabilidad de fin)
        # Instaciar nueva evolution con los jugadores "buenos"

        # Calcular puntuaciones y actualizar ranking
        raise NotImplementedError("Still not implemented")
