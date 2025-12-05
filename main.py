# Por ahora el `main.py` sirve para comprobar que funciona el código

import itertools

from limited_sum import *
from limited_sum import ACTIONS, Evolution, Game, Match, Tournament

# ====================== game.py ======================
# Prints all possible outcomes of the limited-sum game
game = Game()
possible_actions = ACTIONS
for a1, a2 in itertools.product(possible_actions, repeat=2):
    print(f"{(a1, a2)} -> {game.evaluate_result(a1, a2)}")
print("\n ================ \n")
# Output:
# (0, 0) -> (0, 0)
# (0, 1) -> (0, 1)
# ...
# (5, 5) -> (0, 0)

# ====================== player.py / match.py ======================
game = Game()

always0_player = Always0(game, "always0")
always3_player = Always3(game, "always3")
random_player = UniformRandom(game, "random")
focal5_player = Focal5(game, "focal5")
tft_player = TitForTat(game, "tft")
c_infernal = CastigadorInfernal(game, "c_infernal")
d_simpletron = Deterministic_simpletron(game, "d_simpletron")
p_tft = PermissiveTitForTat(game, "PermissiveTitForTat")

# Modifica las siguientes líneas a conveniencia para llevar a cabo distintos tests
match = Match(d_simpletron, focal5_player, stop_prob=0.01, max_rounds=400, error=0.01)
match.play(do_print=True)

# ====================== tournament.py ======================
game = Game()

all_players = (
    always0_player,
    always3_player,
    random_player,
    focal5_player,
    tft_player,
    c_infernal,
    d_simpletron,
    p_tft,
)

tournament = Tournament(
    all_players, stop_prob=0.01, max_rounds=400, error=0.01, repetitions=2
)
tournament.play()
tournament.plot_results()

# ====================== evolution.py ======================
game = Game()

evolution = Evolution(
    all_players,
    stop_prob=0.01,
    max_rounds=400,
    error=0.01,
    repetitions=2,
    generations=25,
    reproductivity=0.2,
    initial_population=20,
)

evolution.play(do_print=True, do_plot=True)
