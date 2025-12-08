from random import choice

from .game import Game
from .player import Player


class HatTricker(Player):
    """
    Player that tries to impose always making 3. It takes the last 3 rounds for insight.
    """

    def __init__(self, game: Game, name: str = "Hat Tricker"):
        super(HatTricker, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        # First three rounds always 3
        play = 3
        if len(opponent.history) >= 3:
            # Detect always 3
            if sum(opponent.history[-3:]) == 9:
                play = 2
            # If opponent is open to cooperate, impose 3
            elif opponent.history[-1] == 2 or opponent.history[-2] == 2:
                play = 3
            else:
                play = choice([2, 3])
        return play