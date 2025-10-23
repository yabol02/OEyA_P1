from abc import ABC, abstractmethod
from random import choice
from typing import Self
from .game import Game


class Player(ABC):
    """
    Abstract base class representing a generic player in a limited-sum game.

    Each player maintains a history of their past actions and must implement
    a strategy for deciding the next move given the opponent's behavior.
    """

    @abstractmethod
    def __init__(self, game: Game, name: str = ""):
        """
        Initializes a player instance.

        :param game: The game that this player will participate in.
        :type game: Game
        :param name: The name of the strategy.
        :type name: str
        """
        self.name = name
        self.game = game

        # Main variable of this class that tores the full history of actions performed by the player.
        # Example: [0, 1, 2, 3] → in the first round the player chose 0, in the second round 1, and so on.
        self.history = []

    @abstractmethod
    def strategy(self, opponent: Self) -> int:
        """
        Defines the strategy used by the player to select an action.

        This method must be implemented by all subclasses and returns the action chosen by the player
        for the next round, possibly based on the opponent's history.

        :param opponent: Another instance of ``Player`` representing the opponent.
        :type opponent: Player
        :return: An integer representing the chosen action (0 to 5).
        :rtype: int
        """
        pass

    def compute_scores(self, opponent: Self) -> tuple[float, float]:
        """
        Computes the payoffs for the current player and an opponent.

        :param opponent: Another instance of ``Player`` representing the opponent.
        :type opponent: Player
        :return: A tuple containing two floats: the current player's payoff and the opponent's payoff.
        :rtype: tuple[float, float]
        """
        if len(self.history) != len(opponent.history):
            raise ValueError("Histories must be of the same length to compute scores.")

        player_score = 0.0
        opponent_score = 0.0

        for p1_action, p2_action in zip(self.history, opponent.history):
            p1_payoff, p2_payoff = self.game.evaluate_result(p1_action, p2_action)
            player_score += p1_payoff
            opponent_score += p2_payoff

        return player_score, opponent_score

    def clean_history(self) -> None:
        """
        Resets the history of the current player.

        :return: None
        :rtype: None
        """
        self.history = []


# ---------------------------------------------------------------------
# Basic strategies for the limited-sum game
# ---------------------------------------------------------------------


class Always0(Player):
    """
    Strategy that always selects action 0.
    """

    def __init__(self, game: Game, name: str = "Always 0"):
        """
        Initializes the Always0 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Always0, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 0 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 0.
        :rtype: int
        """
        return 0


class Always3(Player):
    """
    Strategy that always selects action 3.
    """

    def __init__(self, game: Game, name: str = "Always 3"):
        """
        Initializes the Always3 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Always3, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 3 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 3.
        :rtype: int
        """
        return 3


class UniformRandom(Player):
    """
    Strategy that chooses an action uniformly at random.
    """

    def __init__(self, game: Game, name: str = "Uniform Random"):
        """
        Initializes the UniformRandom player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(UniformRandom, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Chooses an action uniformly at random.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: A random integer between 0 and 5.
        :rtype: int
        """
        return choice(self.game.actions)


class Focal5(Player):
    """
    Strategy that tries to coordinate so that i + j = 5 in each round.
    Several possible implementations exist.
    """

    COORDINATION_ACTION = 3

    def __init__(self, game: Game, name: str = "Focal 5"):
        """
        Initializes the Focal5 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Focal5, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Attempts to coordinate on i + j = 5.

        In the first round, it plays COORDINATION_ACTION (3). In subsequent rounds, it adapts
        based on the opponent's last move to maximize the chances of maintaining the efficient sum of 5.

        - If the opponent played a_opp, the target action is 5 - a_opp.
        - The chosen action is clipped to be between 0 and 5.

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        if not opponent.history:
            return self.COORDINATION_ACTION

        last_opponent_action = opponent.history[-1]
        desired_action = self.game.threshold - last_opponent_action
        action = max(0, min(self.game.threshold, desired_action))

        return action


class TitForTat(Player):
    """
    Reactive strategy inspired by the classic Tit-for-Tat, adapted for the limited-sum game.
    """

    COOPERATIVE_ACTION = 2

    def __init__(self, game: Game, name: str = "Tit for Tat"):
        """
        Initializes the TitForTat player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(TitForTat, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Reacts to the opponent's past actions, rewarding cooperation and punishing greedy behavior (actions above 3).

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        if not opponent.history:
            return self.COOPERATIVE_ACTION

        last_opponent_action = opponent.history[-1]

        return last_opponent_action


class CastigadorInfernal(Player):
    """
    Adaptive strategy for the limited-sum game that balances coordination and self-protection.

    Strategy logic:
        - Starts trying to coordinate on i + j = 5 (efficient outcome).
        - Monitors opponent’s cooperation patterns and adapts accordingly.
        - Uses graduated punishment for greedy behavior.
        - Attempts forgiveness and cooperation recovery.
        - Adjusts strategy based on opponent’s consistency.
    """

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the CastigadorInfernal player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super().__init__(game, name)
        self.cooperation_score = 0  # Tracks opponent's cooperative behavior.
        self.punishment_mode = False
        self.punishment_rounds = 0

    def strategy(self, opponent: Player) -> int:
        """
        Determines the next action based on adaptive cooperation tracking.

        The strategy combines cooperation attempts, punishment for exploitation, and recovery after punishment periods.

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
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

        # Analyze opponent's recent behavior
        recent_rounds = min(5, len(opponent.history))
        recent_actions = opponent.history[-recent_rounds:]
        avg_recent = sum(recent_actions) / len(recent_actions)

        # Punishment phase
        if self.punishment_mode:
            self.punishment_rounds += 1
            if self.punishment_rounds <= 2:
                return last_opponent # Vamos a hacer que el castigo sea Tic of Tat
            else:
                self.punishment_mode = False
                self.punishment_rounds = 0
                return 2

        # Detect consistent greedy behavior
        if last_opponent > 3 and avg_recent > 3.5:
            self.punishment_mode = True
            self.punishment_rounds = 0
            return last_opponent # Vamos a hacer que el castigo sea Tic of Tat

        # Normal coordination attempt
        if last_opponent <= 3:
            return max(0, min(5, 5 - last_opponent))

        # Default fallback
        return 2
