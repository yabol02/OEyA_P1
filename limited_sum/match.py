from .player import Player

class Match:

    # Este método ya está implementado
    def __init__(self, player_1: Player,
                       player_2: Player,
                       n_rounds: int = 100,
                       error: float = 0.0):
        """
        Match class to represent an iterative limited-sum game

        Parameters:
            - player_1 (Player): first player of the match
            - player_2 (Player): second player of the match
            - n_rounds (int = 100): number of rounds in the match
            - error (float = 0.0): error probability (on a 0-1 scale).
        """

        assert n_rounds > 0, "'n_rounds' should be greater than 0"

        self.player_1 = player_1
        self.player_2 = player_2
        self.n_rounds = n_rounds
        self.error = error

        self.score = (0.0, 0.0)  # this variable will store the final result of
                                 # the match, once the 'play()' function has
                                 # been called. The two values of the tuple
                                 # correspond to the points scored by the first
                                 # and second player, respectively.


    def play(self, do_print: bool = False) -> None:
        """
        Main call of the class. Play the match.
        Stores the final result in 'self.score'

        Parameters
            - do_print (bool = False): if True, should print the ongoing
            results at the end of each round (i.e. print round number, last
            actions of both players and ongoing score).
        """
        raise NotImplementedError