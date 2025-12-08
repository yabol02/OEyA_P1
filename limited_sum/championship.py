import numpy as np
import pandas as pd

from .evolution import ProportionalEvolution
from .player import (Always0, Always3, CastigadorInfernal, Focal5, Player,
                     TitForTat, UniformRandom)
from .tournament import Tournament


class Championship:
    points_1st_phase = {1: 24, 2: 17, 3: 12, 4: 8, 5: 4, 6: 4}
    points_2nd_phase = {1: 24, 2: 17, 3: 12}
    points_3rd_phase = {1: 12, 2: 8, 3: 4}

    def __init__(
        self,
        players: tuple[Player, ...],
        max_rounds: int = 400,
        stop_prob: float = 0.01,
        error: float = 0.01,
        repetitions: int = 2,
        generations: int = 10,
        initial_population: int = 20,
    ):
        """
        Initializes a Championship with the given players and configuration parameters.

        :param players: Tuple of Player instances participating in the championship. All names must be unique.
        :type players: tuple[Player, ...]
        :param max_rounds: Maximum number of rounds for each match in the tournament phases.
        :type max_rounds: int
        :param stop_prob: Probability of stopping a match early.
        :type stop_prob: float
        :param error: Noise probability applied to player actions.
        :type error: float
        :param repetitions: Number of repetitions for matches in the tournament phase.
        :type repetitions: int
        :param generations: Number of generations in evolutionary phases.
        :type generations: int
        :param initial_population: Initial population size in evolutionary phases.
        :type initial_population: int
        :param save_results: Whether to save intermediate results, currently unused.
        :type save_results: bool
        """
        self.players = players
        assert len(players) == len(
            set(p.name for p in players)
        ), "Player names must be unique !!!"
        self.max_rounds = max_rounds
        self.stop_prob = stop_prob
        self.error = error
        self.repetitions = repetitions
        self.generations = generations
        self.initial_population = initial_population
        self.ranking = {player.name: 0 for player in players}

    def play(self, do_print: bool = False, return_dfs=False):
        """
        Executes the full championship through its three phases. Prints intermediate rankings and returns
        raw DataFrames if requested.

        :param do_print: If True, shows the ranking after each phase.
        :type do_print: bool
        :param return_dfs: If True, returns the raw DataFrames from each phase.
        :type return_dfs: bool
        :return: If return_dfs is True, a tuple (df_1, df_2, df_3) with raw data of the three phases.
        """
        print("\n" + "=" * 32)
        print("CHAMPIONSHIP TOURNAMENT STARTING")
        print("The players are:")
        for player in self.players:
            print(f"- {player}")
        print("=" * 32 + "\n")

        df_1 = self._first_phase(return_dfs=return_dfs)
        if do_print:
            self._print_ranking("First Phase")

        df_2 = self._second_phase(return_dfs=return_dfs)
        if do_print:
            self._print_ranking("Second Phase")

        df_3 = self._third_phase(return_dfs=return_dfs)
        if do_print:
            self._print_ranking("Third Phase")

        self._podium()
        if return_dfs:
            return df_1, df_2, df_3

    def _update_ranking(self, results: pd.DataFrame, points_map: dict, phase_name: str):
        """
        Updates the ranking based on the results of a tournament phase.

        :param results: DataFrame with 'player' and 'scores', sorted by average score.
        :type results: pd.DataFrame
        :param points_map: Dictionary of points by position (1, 2, 3, ...).
        :type points_map: dict
        """
        max_rank_points = max(points_map.keys()) if points_map else 0
        print(f"\nUpdating ranking after {phase_name}\n")
        for rank, row in results.iterrows():
            self.ranking[row["player"].name] += points_map.get(rank + 1, 0)
            print(
                f"Player {row['player'].name} gets {points_map.get(rank + 1, 0)} points for position {rank + 1}."
            )
            if rank + 1 >= max_rank_points:
                print("The rest of the players get 0 points.")
                break
        print()

    def _process_evolution_results(
        self, evolution_history: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Processes the evolution history produced by an evolutionary phase. Computes for each player the
        last generation where it had positive population and its average population across generations.

        :param evolution_history: A DataFrame-like structure where each column is a player and each row
            represents its population in a generation.
        :type evolution_history: pd.DataFrame
        :return: DataFrame with columns 'player' and 'score', sorted by survival depth and average score.
        :rtype: pd.DataFrame
        """
        data = list()
        for player, counts in evolution_history.items():
            try:
                last_alive = max(i for i, c in enumerate(counts) if c > 0)
            except ValueError:
                last_alive = -1

            avg_score = sum(counts) / len(counts)
            data.append(
                {"player": player, "last_alive": last_alive, "score": avg_score}
            )

        df = pd.DataFrame(data)
        df = df.sort_values(
            by=["last_alive", "score"], ascending=[False, False]
        ).reset_index(drop=True)

        df = df[["player", "score"]]

        return df

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

        :param phase_name: Name of the phase just completed.
        :type phase_name: str
        """
        print(f"\n{phase_name} completed. Current Ranking:")
        sorted_ranking = dict(
            sorted(self.ranking.items(), key=lambda item: item[1], reverse=True)
        )
        for player, points in sorted_ranking.items():
            print(f"  {player}: {points} points")
        print("-" * 30)

    def _first_phase(self, return_dfs: bool = False):
        """
        Runs the first phase of the championship using a standard tournament. Sorts results, updates
        the ranking and optionally returns the raw DataFrame before processing.

        :param return_dfs: If True, returns the raw tournament DataFrame.
        :type return_dfs: bool
        :return: The raw DataFrame with detailed results if return_dfs is True.
        """
        tournament = Tournament(
            players=self.players,
            stop_prob=self.stop_prob,
            max_rounds=self.max_rounds,
            error=self.error,
            repetitions=self.repetitions,
        )

        # Play tournament and process results
        res1 = tournament.play_trace()
        if return_dfs:
            df1 = res1.copy(deep=True)
        res1 = self._sort_results(res1)

        # Update ranking based on self.points_1st_phase
        self._update_ranking(res1, self.points_1st_phase, "First Phase (Tournament)")
        if return_dfs:
            return df1

    def _second_phase(self, return_dfs: bool = False):
        """
        Runs the second phase of the championship using proportional evolution. Processes the evolutionary
        history, updates the ranking and optionally returns the raw history DataFrame.

        :param return_dfs: If True, returns the raw evolution DataFrame.
        :type return_dfs: bool
        :return: The raw DataFrame with detailed evolution data if return_dfs is True.
        """
        evolution = ProportionalEvolution(
            players=self.players,
            stop_prob=self.stop_prob,
            max_rounds=self.max_rounds,
            error=self.error,
            repetitions=self.repetitions,
            generations=self.generations,
            initial_population=self.initial_population,
        )
        if return_dfs:
            res2 = evolution.play_trace()
            df2 = res2.copy(deep=True)
        else:
            evolution.play()
        res2 = self._process_evolution_results(evolution.history)
        self._update_ranking(res2, self.points_2nd_phase, "Second Phase (Evolution)")
        if return_dfs:
            return df2

    def _third_phase(self, return_dfs: bool = False):
        """
        Runs the third phase of the championship, where players evolve in a more complex environment that
        includes additional fixed strategies. Results are filtered to include only original players before
        updating the ranking.

        :param return_dfs: If True, returns the raw evolution DataFrame.
        :type return_dfs: bool
        :return: The raw DataFrame with detailed evolution data if return_dfs is True.
        """
        game = self.players[0].game
        complex_environment_players = (
            Always0(game),
            Always3(game),
            UniformRandom(game),
            Focal5(game),
            TitForTat(game),
            CastigadorInfernal(game),
        )
        evolution = ProportionalEvolution(
            players=self.players + complex_environment_players,
            stop_prob=self.stop_prob,
            max_rounds=self.max_rounds,
            error=self.error,
            repetitions=self.repetitions,
            generations=self.generations,
            initial_population=self.initial_population,
        )
        if return_dfs:
            df3 = evolution.play_trace()
        else:
            evolution.play()
        res3 = self._process_evolution_results(evolution.history)
        res3 = res3[res3["player"].isin(self.players)]
        self._update_ranking(
            res3,
            self.points_3rd_phase,
            "Third Phase (Evolution in complex environment)",
        )
        if return_dfs:
            return df3

    def _podium(self):
        """
        Prints the final ranking of the championship showing the total accumulated points for all players.
        """
        print("\nFinal Ranking:")
        sorted_ranking = dict(
            sorted(self.ranking.items(), key=lambda item: item[1], reverse=True)
        )
        for rank, (player, points) in enumerate(sorted_ranking.items(), start=1):
            print(f"  {rank}. {player}: {points} points")
        print("-" * 30)
