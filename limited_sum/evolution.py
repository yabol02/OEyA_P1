import copy
import itertools
import math
import matplotlib.pyplot as plt
import numpy as np

from .match import Match
from .player import Player


class Evolution:
    def __init__(
        self,
        players: tuple[Player, ...],
        n_rounds: int = 100,
        error: float = 0.0,
        repetitions: int = 2,
        generations: int = 100,
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
        self.n_rounds = n_rounds
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

    def natural_selection(
        self, result_tournament: dict[Player, float]
    ) -> tuple[list, list]:
        """
        Applies the natural selection process based on tournament results.

        Removes the least successful players and reproduces the top-performing ones.
        Returns an updated ranking reflecting the evolutionary changes.

        :param result_tournament: Dictionary mapping players to their total scores.
        :type result_tournament: dict[Player, float]
        :return: A tuple of two lists: the new population of players and their corresponding scores.
        :rtype: tuple[list, list]
        """
        sorted_players = sorted(
            result_tournament.items(), key=lambda item: item[1], reverse=True
        )

        current_population = [item[0] for item in sorted_players]
        current_scores = [item[1] for item in sorted_players]

        replacements = self.repr_int
        parents = current_population[:replacements]
        survivors = current_population[:-replacements]
        survivors_scores = current_scores[:-replacements]

        offspring = []
        for parent in parents:
            new_offspring = copy.deepcopy(parent)
            new_offspring.clean_history()
            offspring.append(new_offspring)

        new_population = survivors + offspring
        new_scores = [0] * len(new_population)

        return new_population, new_scores

    def count_strategies(self) -> dict[str, int]:
        """
        Counts the number of living individuals for each strategy.

        This method analyzes the ``self.ranking`` dictionary and computes
        how many instances of each player type remain alive.

        :return: Dictionary mapping player strategy names to their current population count.
        :rtype: dict[str, int]
        """
        counts = {}

        for player_instance in self.ranking.keys():
            strategy_name = player_instance.name
            counts[strategy_name] = counts.get(strategy_name, 0) + 1

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
        self.count_evolution = {}

        initial_counts = self.count_strategies()
        for name, count in initial_counts.items():
            self.count_evolution[name] = [count]

        current_population_list = list(self.ranking.keys())
        for generation in range(1, self.generations + 1):
            current_ranking = {player: 0.0 for player in current_population_list}
            for player_1, player_2 in itertools.combinations(
                current_population_list, 2
            ):
                for _ in range(self.repetitions):
                    match = Match(
                        player_1=player_1,
                        player_2=player_2,
                        n_rounds=self.n_rounds,
                        error=self.error,
                    )
                    match.play(do_print=False)
                    score_p1, score_p2 = match.score

                    current_ranking[player_1] += score_p1
                    current_ranking[player_2] += score_p2

                    player_1.clean_history()
                    player_2.clean_history()

            new_population_list, _ = self.natural_selection(current_ranking)
            current_population_list = new_population_list

            current_counts = {}
            for player_instance in current_population_list:
                name = player_instance.name
                current_counts[name] = current_counts.get(name, 0) + 1

            for name, count in current_counts.items():
                self.count_evolution.setdefault(name, []).append(count)

            for initial_player in self.players:
                if initial_player.name not in self.count_evolution:
                    self.count_evolution[initial_player.name] = [0] * generation

            if do_print:
                print(f"\n--- GENERATION {generation:03d} ---")
                print("Population count:", current_counts)

        print("\n" + "=" * 50)
        print(f"EVOLUTIONARY TOURNAMENT FINISHED after {self.generations} generations.")
        print("=" * 50)

        self.ranking = current_ranking

        if do_plot:
            self.stackplot(self.count_evolution)

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

        for i, name in enumerate(count_evolution.keys()):
            plt.plot([], [], label=name, color=COLORS[i % len(COLORS)])

        plt.stackplot(
            list(range(self.generations + 1)),
            np.array(list(count_evolution.values())),
            colors=COLORS,
        )

        plt.legend()
        plt.show()
