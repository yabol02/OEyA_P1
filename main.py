# Por ahora el `main.py` sirve para comprobar que funciona el código

import itertools

from limited_sum import Evolution
from limited_sum import ACTIONS, Game
from limited_sum import Match
from limited_sum import Always0, Always3, UniformRandom, Focal5, TitForTat
from limited_sum import Tournament

# ====================== game.py ======================
# Prints all possible outcomes of the limited-sum game
game = Game()
possible_actions = ACTIONS
for a1, a2 in itertools.product(possible_actions, repeat=2):
    print(f"{(a1, a2)} -> {game.evaluate_result(a1, a2)}")

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

# Modifica las siguientes líneas a conveniencia para llevar a cabo distintos tests
match = Match(always0_player, focal5_player, n_rounds=10, error=0.2)
match.play(do_print=True)

# ====================== tournament.py ======================
game = Game()

always0_player = Always0(game, "always0")
always3_player = Always3(game, "always3")
random_player = UniformRandom(game, "random")
focal5_player = Focal5(game, "focal5")
tft_player = TitForTat(game, "tft")

all_players = (always0_player, always3_player, random_player, focal5_player, tft_player)

tournament = Tournament(all_players, n_rounds=10, error=0.0, repetitions=1)
tournament.play()
tournament.plot_results()

# ====================== evolution.py ======================
game = Game()

always0_player = Always0(game, "always0")
random_player = UniformRandom(game, "random")
focal5_player = Focal5(game, "focal5")

all_players = (always0_player, random_player, focal5_player)

evolution = Evolution(
    all_players,
    n_rounds=10,
    error=0.00,
    repetitions=1,
    generations=10,
    reproductivity=0.2,
    initial_population=(15, 5, 5),
)

evolution.play(do_print=True, do_plot=True)
