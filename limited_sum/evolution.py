import copy
import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from .player import Player
from .tournament import Tournament


class Evolution:
    def __init__(
        self,
        players: tuple[Player, ...],
        stop_prob: float = 0.0,
        max_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 1,
        generations: int = 10,
        reproductivity: float = 0.05,
        initial_population: tuple[int, ...] | int = 100,
    ):
        """
        Represents an evolutionary tournament, where players evolve through
        repeated matches and natural selection.

        :param players: Tuple of players that will participate in the tournament.
        :type players: tuple[Player, ...]
        :param n_rounds: Number of rounds in each game.
        :type n_rounds: int
        :param error: Probability of making an error (0–1 scale).
        :type error: float
        :param repetitions: Number of games each player plays against every other player.
        :type repetitions: int
        :param generations: Number of generations to simulate.
        :type generations: int
        :param reproductivity: Fraction (0–1) of the population that is replaced
            in each generation by offspring of the top-performing players.
        :type reproductivity: float
        :param initial_population: Either the total population size (int) or a tuple
            specifying the initial number of individuals per player.
        :type initial_population: tuple[int, ...] | int
        """
        self.players = players
        self.stop_prob = stop_prob
        self.max_rounds = max_rounds
        self.error = error
        self.repetitions = repetitions
        self.generations = generations
        self.reproductivity = reproductivity

        if isinstance(initial_population, int):
            self.initial_population = [
                math.floor(initial_population / len(self.players))
                for _ in range(len(self.players))
            ]
        else:
            self.initial_population = initial_population

        self.total_population = sum(self.initial_population)
        self.repr_int = int(self.total_population * self.reproductivity)

        # Dictionary storing the current population (as Player copies) and their accumulated scores within each generation.
        self.ranking = {
            copy.deepcopy(player): 0.0
            for i, player in enumerate(self.players)
            for _ in range(self.initial_population[i])
        }
        # Dictionary storing the cumulative ranking across generations for processing later
        self.cumulative_ranking = copy.deepcopy(self.ranking)

        # TODO: Do we need both?
        self._head_to_head_rewards = []
        self.head_to_head_rewards = None

    def natural_selection(
        self, result_tournament: dict[Player, float]
    ) -> dict[Player, float]:
        """
        Applies the natural selection process based on tournament results.

        Removes the least successful players and reproduces the top-performing ones.
        Returns an updated ranking reflecting the evolutionary changes.

        :param result_tournament: Dictionary mapping players to their total scores.
        :type result_tournament: dict[Player, float]
        :return: A tuple of two lists: the new population of players and their corresponding scores.
        :rtype: dict[Player, float]
        """
        sorted_players = dict(
            sorted(result_tournament.items(), key=lambda item: item[1], reverse=True)
        )

        current_population, current_scores = map(
            list, zip(*[(player, score) for player, score in sorted_players.items()])
        )

        parents = current_population[: self.repr_int]
        survivors = current_population[: -self.repr_int]
        # survivors_scores = current_scores[:-self.repr_int]

        offspring = []
        for parent in parents:
            new_player = copy.deepcopy(parent)
            new_player.clean_history()
            offspring.append(new_player)

        new_population = survivors + offspring
        new_scores = [0] * len(new_population)

        return dict(zip(new_population, new_scores))

    def count_strategies(self) -> dict[str, int]:
        """
        Counts the number of living individuals for each strategy.

        This method analyzes the ``self.ranking`` dictionary and computes
        how many instances of each player type remain alive.

        :return: Dictionary mapping player strategy names to their current population count.
        :rtype: dict[str, int]
        """
        counts = dict()

        for player_instance in self.ranking.keys():
            strategy_name = player_instance.name
            counts[strategy_name] = counts.get(strategy_name, 0) + 1

        for initial_player in self.players:
            if initial_player.name not in counts:
                counts[initial_player.name] = 0

        return counts

    def play(self, do_print: bool = False, do_plot: bool = False) -> None:
        """
        Simulates the full evolutionary tournament.

        This method performs the evolutionary process across several generations,
        where each generation includes all matches, ranking updates, and
        natural selection.

        :param do_print: If True, prints intermediate results after each generation.
        :type do_print: bool
        :param do_plot: If True, plots the intermediate results as a stackplot.
        :type do_plot: bool
        :return: None
        :rtype: None
        """
        count_evolution = dict()

        initial_counts = self.count_strategies()
        for name, count in initial_counts.items():
            count_evolution[name] = [count]

        progressbar = tqdm(
            iterable=range(1, self.generations + 1),
            desc="Evolution progress",
            position=0,
        )
        for generation in progressbar:
            tournament = Tournament(
                players=list(self.ranking.keys()),
                stop_prob=self.stop_prob,
                max_rounds=self.max_rounds,
                error=self.error,
                repetitions=self.repetitions,
            )

            tournament.play(ext_progress=True)
            self.ranking = self.natural_selection(tournament.ranking)
            current_counts = self.count_strategies()

            for initial_player in self.players:
                if initial_player.name not in current_counts:
                    count_evolution[initial_player.name] += [0]
                else:
                    count_evolution[initial_player.name].append(
                        current_counts[initial_player.name]
                    )

            if do_print:
                tqdm.write(f"\n--- GENERATION {generation:03d} ---")
                tqdm.write(f"Population count: {current_counts}")

            if len(current_counts) == 1:
                break

        print("\n" + "=" * 50)
        print(f"EVOLUTIONARY TOURNAMENT FINISHED after {self.generations} generations.")
        print("=" * 50)

        if do_plot:
            self.stackplot(count_evolution)

    def play_trace(self, do_plot: bool = False) -> pd.DataFrame:
        """
        Simulates the full evolutionary tournament.

        This method performs the evolutionary process across several generations,
        where each generation includes all matches, ranking updates, and natural selection.

        Ir also returns a dataframe with all the information.

        :param do_plot: If True, plots the intermediate results as a stackplot.
        :type do_plot: bool
        :return: A pandas DataFrame containing the full trace of the evolutionary tournament.
        :rtype: pd.DataFrame
        """
        count_evolution = dict()
        all_tournament_results = list()

        initial_counts = self.count_strategies()
        for name, count in initial_counts.items():
            count_evolution[name] = [count]

        progressbar = tqdm(
            iterable=range(1, self.generations + 1),
            desc="Evolution progress",
            position=0,
        )
        for generation in progressbar:
            tournament = Tournament(
                players=list(self.ranking.keys()),
                stop_prob=self.stop_prob,
                max_rounds=self.max_rounds,
                error=self.error,
                repetitions=self.repetitions,
            )

            tournament_results = tournament.play_trace(ext_progress=True)
            self.ranking = self.natural_selection(tournament.ranking)
            current_counts = self.count_strategies()

            for initial_player in self.players:
                if initial_player.name not in current_counts:
                    count_evolution[initial_player.name] += [0]
                else:
                    count_evolution[initial_player.name].append(
                        current_counts[initial_player.name]
                    )

            tournament_results["generation"] = generation
            all_tournament_results.append(tournament_results)

            if len(current_counts) == 1:
                break

        print("\n" + "=" * 50)
        print(f"EVOLUTIONARY TOURNAMENT FINISHED after {self.generations} generations.")
        print("=" * 50)

        if do_plot:
            self.stackplot(count_evolution)

        return pd.concat(all_tournament_results, ignore_index=True)

    def update_cumulative_ranking(self, current_ranking):
        for k, v in current_ranking.items():
            self.cumulative_ranking[k] = v

    def get_head_to_head_rewards(self):
        if len(self._head_to_head_rewards) == 0:
            return None
        else:
            if self.head_to_head_rewards is None:
                self.head_to_head_rewards = pd.DataFrame(self._head_to_head_rewards)

            return self.head_to_head_rewards

    def stackplot(self, count_evolution: dict[str, list]) -> None:
        """
        Plots a stackplot showing the evolution of player populations over generations.

        The x-axis represents the generations, and the y-axis shows the cumulative
        number of individuals per strategy.

        :param count_evolution: Dictionary mapping strategy names to a list of
            population counts per generation.
        :type count_evolution: dict[str, list]
        :return: None
        :rtype: None
        """
        COLORS = ["blue", "green", "red", "cyan", "magenta", "yellow", "black"]

        target_length = self.generations + 1
        padded_counts = {}
        for name, counts in count_evolution.items():
            if len(counts) < target_length:
                padding_needed = target_length - len(counts)
                padded_counts[name] = counts + [0] * padding_needed
            else:
                padded_counts[name] = counts[:target_length]

        data_to_plot = list(padded_counts.values())
        names_to_plot = list(padded_counts.keys())

        for i, name in enumerate(names_to_plot):
            plt.plot([], [], label=name, color=COLORS[i % len(COLORS)])

        plt.stackplot(
            list(range(target_length)),
            np.array(data_to_plot),
            colors=COLORS,
        )

        plt.xlabel("Generación")
        plt.ylabel("Población Total")
        plt.title(
            f"Evolución de la Población de Estrategias ({self.generations} Generaciones)"
        )

        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.show()
