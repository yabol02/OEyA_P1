"""
Docstring for OEyA_P1.limited_sum.final_tournament

Class for playing the final tournament of the practice. This tournament will evaluate our players performance.

"""

from .player import Player
from .game import Game
from .match import Match
from .tournament import Tournament


class FinalTournament():
    def __init__(
        self,
        players: tuple[Player, ...],
        all_players: tuple[Player, ...],
        max_rounds: int = 400,
        end_match_possibility: float = 0.01,
        error: float = 0.01,
        repetitions: int = 2,
        representatives: int = 5,
        
    ):
        self.players = players
        self.all_players = all_players 
        self.max_rounds = max_rounds
        self.end_match_possibility = end_match_possibility
        self.error = error
        self.repetitions = repetitions
        self.points_table = {}
        self.ranking = {player: 0 for player in all_players}

    def first_tournament(self):
        points = { # maybe change it to a list
            1: 24,
            2: 17,
            3: 12,
            4: 8,
            5: 4,
            6: 4
        }
        # Pasar Match con personalizacione (400 rondas, 0.01 probabilidad de fin)
        tournament = Tournament(
            players=self.players,
            n_rounds=self.max_rounds,
            error=self.error,
            repetitions=self.repetitions,
        )

        tournament.play_trace()
        # Guardar datos de la evolucion 

        # Calcular puntuaciones y actualizar ranking
        pass

    def second_tournament(self):
        points = { # maybe change it to a list
            1:24,
            2:17,
            3:12
        }
        # Pasar Match con personalizacione (400 rondas, 0.01 probabilidad de fin)
        # Instaciar nueva evolution con los jugadores "buenos"

        # Calcular puntuaciones y actualizar ranking
        pass

    def third_tournament(self):
        points = { # maybe change it to a list
            1:12,
            2:8,
            3:4
        }
        # Pasar Match con personalizacione (400 rondas, 0.01 probabilidad de fin)
        # Instaciar nueva evolution con los jugadores "buenos"

        # Calcular puntuaciones y actualizar ranking
        pass