from abc import ABC, abstractmethod
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

        # Main variable of this class.
        # Stores the full history of actions performed by the player.
        # Example: [0, 1, 2, 3] → in the first round the player chose 0,
        # in the second round 1, and so on.
        self.history = []

    @abstractmethod
    def strategy(self, opponent: Self) -> int:
        """
        Defines the strategy used by the player to select an action.

        This method must be implemented by all subclasses and returns
        the action chosen by the player for the next round, possibly based
        on the opponent's history.

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
        :return: A tuple containing two floats: the current player's payoff
            and the opponent's payoff.
        :rtype: tuple[float, float]
        """
        raise NotImplementedError

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

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the Always0 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        raise NotImplementedError

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 0 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 0.
        :rtype: int
        """
        raise NotImplementedError


class Always3(Player):
    """
    Strategy that always selects action 3.
    """

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the Always3 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        raise NotImplementedError

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 3 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 3.
        :rtype: int
        """
        raise NotImplementedError


class UniformRandom(Player):
    """
    Strategy that chooses an action uniformly at random.
    """

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the UniformRandom player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        raise NotImplementedError

    def strategy(self, opponent: Player) -> int:
        """
        Chooses an action uniformly at random.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: A random integer between 0 and 5.
        :rtype: int
        """
        raise NotImplementedError


class Focal5(Player):
    """
    Strategy that tries to coordinate so that i + j = 5 in each round.
    Several possible implementations exist.
    """

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the Focal5 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        raise NotImplementedError

    def strategy(self, opponent: Player) -> int:
        """
        Attempts to coordinate on i + j = 5.

        In the first round, it plays 2. In subsequent rounds, it adapts
        based on the opponent's behavior to maximize the chances of
        maintaining the efficient sum of 5.

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        raise NotImplementedError


class TitForTat(Player):
    """
    Reactive strategy inspired by the classic Tit-for-Tat,
    adapted for the limited-sum game.
    """

    def __init__(self, game: Game, name: str = ""):
        """
        Initializes the TitForTat player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        raise NotImplementedError

    def strategy(self, opponent: Player) -> int:
        """
        Reacts to the opponent's past actions, rewarding cooperation
        and punishing greedy behavior (actions above 3).

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        raise NotImplementedError


class CastigadorInfernal(Player):
    """
    Adaptive strategy for the limited-sum game that balances coordination
    and self-protection.

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

        The strategy combines cooperation attempts, punishment for exploitation,
        and recovery after punishment periods.

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
                return 0
            else:
                self.punishment_mode = False
                self.punishment_rounds = 0
                return 2

        # Detect consistent greedy behavior
        if last_opponent > 3 and avg_recent > 3.5:
            self.punishment_mode = True
            self.punishment_rounds = 0
            return 0

        # Normal coordination attempt
        if last_opponent <= 3:
            return max(0, min(5, 5 - last_opponent))

        # Default fallback
        return 2
