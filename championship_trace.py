import argparse
import datetime

from limited_sum import *
from limited_sum import (ACTIONS, Championship, Evolution, Game, Match,
                         Tournament)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the Championship with specified output folder.")
    parser.add_argument(
        "output_folder",        
        type=str,
        help="Mandatory: Path to the folder where results will be saved."
        
    )
    return parser.parse_args()

args = parse_arguments()
output_folder = args.output_folder

# print(f"Output folder: {output_folder}")
# exit(1)


game = Game()

# ====================== championship.py ======================
from limited_sum import (AdaptivePavlov, AgenteAstuto, BinarySunset,
                         ContriteTitForTat, CopyCat, Detective,
                         DeterministicSimpletron, GenerousTitForTat,
                         GrimTrigger, HatTricker, PermissiveTitForTat,
                         Random23, WeightedRandom23, WSLS_Adapted)

players = (AdaptivePavlov(game), AgenteAstuto(game), BinarySunset(game),
                    ContriteTitForTat(game), CopyCat(game), Detective(game),
                    DeterministicSimpletron(game), GenerousTitForTat(game),
                    GrimTrigger(game), HatTricker(game), PermissiveTitForTat(game),
                    Random23(game), WeightedRandom23(game), WSLS_Adapted(game))

championship = Championship(
    players=players,
    max_rounds=400,
    stop_prob=0.01,
    error=0.01,
    repetitions=2,
    save_results=True
)
championship.play()

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

championship.results_first_phase.to_csv(f"{output_folder}/{timestamp}_first_phase.csv", index=False, sep=';')
championship.results_second_phase.to_csv(f"{output_folder}/{timestamp}_second_phase.csv", index=False, sep=';')
championship.results_third_phase.to_csv(f"{output_folder}/{timestamp}_third_phase.csv", index=False, sep=';')
