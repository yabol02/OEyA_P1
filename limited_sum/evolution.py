import copy
import math
import matplotlib.pyplot as plt
import numpy as np

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

        # Dictionary storing the current population (as Player copies)
        # and their accumulated scores within each generation.
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
        raise NotImplementedError

    def count_strategies(self) -> dict[str, int]:
        """
        Counts the number of living individuals for each strategy.

        This method analyzes the ``self.ranking`` dictionary and computes
        how many instances of each player type remain alive. Useful for
        tracking population dynamics or generating plots.

        :return: Dictionary mapping player strategy names to their current population count.
        :rtype: dict[str, int]
        """
        raise NotImplementedError

    def play(self, do_print: bool = False) -> None:
        """
        Simulates the full evolutionary tournament.

        This method performs the evolutionary process across several generations,
        where each generation includes all matches, ranking updates, and
        natural selection. It should update the internal population structure.

        :param do_print: If True, prints intermediate results after each generation,
            including the generation number and the number of individuals per strategy.
        :type do_print: bool
        :return: None
        :rtype: None
        """
        raise NotImplementedError

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
