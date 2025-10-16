from abc import ABC, abstractmethod
from typing import Self
from .game import Game

class Player(ABC):

    # Este método ya está implementado
    @abstractmethod
    def __init__(self, game: Game, name: str = ""):
        """
        Abstract class that represents a generic player

        Parameters:
            - name (str): the name of the strategy
            - game (Game): the game that this player will play
        """

        self.name = name
        self.game = game

        self.history  = []  # This is the main variable of this class. It is
                            # intended to store all the history of actions
                            # performed by this player.
                            # Example: [0, 1, 2, 3] <- So far, the
                            # interaction lasts four rounds. In the first one,
                            # this player chose 0. In the second, 1. Etc.


    # Este método ya está implementado
    @abstractmethod
    def strategy(self, opponent: Self) -> int:
        """
        Main call of the class. Gives the action for the following round of the
        interaction, based on the history

        Parameters:
            - opponent (Player): is another instance of Player.

        Results:
            - An integer representing the action (0 to 5)
        """
        pass


    def compute_scores(self, opponent: Self) -> tuple[float, float]:
        """
        Compute the scores for a given opponent

        Parameters:
            - opponent (Player): is another instance of Player.

        Results:
            - A tuple of two floats, where the first value is the current
            player's payoff, and the second value is the opponent's payoff.
        """
        raise NotImplementedError


    # Este método ya está implementado
    def clean_history(self):
        """Resets the history of the current player"""
        self.history = []


# A continuación se representan las estrategias básicas para el juego de suma limitada

class Always0(Player):

    def __init__(self, game: Game, name: str = ""):
        """Always chooses 0"""
        raise NotImplementedError


    def strategy(self, opponent: Player) -> int:
        """Always chooses 0"""
        raise NotImplementedError


class Always3(Player):

    def __init__(self, game: Game, name: str = ""):
        """Always chooses 3"""
        raise NotImplementedError


    def strategy(self, opponent: Player) -> int:
        """Always chooses 3"""
        raise NotImplementedError


class UniformRandom(Player):

    def __init__(self, game: Game, name: str = ""):
        """Chooses uniformly at random"""
        raise NotImplementedError


    def strategy(self, opponent: Player) -> int:
        """Chooses uniformly at random"""
        raise NotImplementedError


class Focal5(Player):

    def __init__(self, game: Game, name: str = ""):
        """Tries to coordinate on i+j=5. Several logics possible."""
        raise NotImplementedError


    def strategy(self, opponent: Player) -> int:
        """First round: 2, then adapts based on opponent trying to maximize the
        chances of establishing a 5-way split in each round."""
        raise NotImplementedError


class TitForTat(Player):

    def __init__(self, game: Game, name: str = ""):
        """Tit-for-tat adapted to the JCMA. Several logics possible."""
        raise NotImplementedError


    def strategy(self, opponent: Player) -> int:
        """Similar to Focal5, but reactive with opponent's actions above 3."""
        raise NotImplementedError
    
# Estrategia del Profesor
class CastigadorInfernal(Player):
    """
    Adaptive strategy for the limited-sum game that balances coordination and self-protection.

    Strategy:
    - Starts trying to coordinate on i+j=5 (efficient outcome)
    - Monitors opponent's cooperation patterns and adapts accordingly
    - Uses graduated punishment for greedy behavior
    - Attempts forgiveness and cooperation recovery
    - Adjusts strategy based on opponent's consistency
    """

    def __init__(self, game: Game, name: str = ""):
        super().__init__(game, name)
        self.cooperation_score = 0  # Track opponent's cooperative behavior
        self.punishment_mode = False
        self.punishment_rounds = 0

    def strategy(self, opponent: Player) -> int:
        """
        Adaptive strategy with cooperation tracking and graduated response
        """
        # First round: start with 2 (middle ground)
        if not self.history:
            return 2

        last_opponent = opponent.history[-1]

        # Update cooperation tracking
        if last_opponent <= 3:
            self.cooperation_score += 1
        else:
            self.cooperation_score -= 2

        # Analyze opponent's recent pattern (last 5 rounds)
        recent_rounds = min(5, len(opponent.history))
        recent_actions = opponent.history[-recent_rounds:]
        avg_recent = sum(recent_actions) / len(recent_actions)

        # Simplified punishment mechanism
        if self.punishment_mode:
            self.punishment_rounds += 1
            # Simple punishment: play 0 for 2 rounds, then try to recover
            if self.punishment_rounds <= 2:
                return 0
            else:
                # Reset and try to recover cooperation
                self.punishment_mode = False
                self.punishment_rounds = 0
                return 2

        # Detect consistently greedy behavior
        if last_opponent > 3 and avg_recent > 3.5:
            self.punishment_mode = True
            self.punishment_rounds = 0
            return 0

        # Normal coordination attempt
        if last_opponent <= 3:
            # Try to maintain sum=5
            return max(0, min(5, 5 - last_opponent))

        # Default fallback
        return 2
