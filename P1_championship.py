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
from limited_sum import (LOLA, WSLS, AdaptiveAspiration, AdaptivePavlov,
                         BinarySunset, CleverAgent, ContriteTitForTat, CopyCat,
                         DeterministicSimpletron, Enforcer, Fictitious,
                         FictitiousSoftmax, GenerousTitForTat, GreedyBayes,
                         GrimTrigger, HatTricker, PermissiveTitForTat,
                         Random23, StrongAWSLS, WeightedRandom23, ZDExtortion)

players = (
    StrongAWSLS(game),
    AdaptivePavlov(game),
    CleverAgent(game),
    BinarySunset(game),
    ContriteTitForTat(game),
    CopyCat(game),
    DeterministicSimpletron(game),
    GenerousTitForTat(game),
    GrimTrigger(game),
    HatTricker(game),
    PermissiveTitForTat(game),
    Random23(game),
    WeightedRandom23(game),
    WSLS(game),
    FictitiousSoftmax(game, tau=0.25),
    GreedyBayes(game),
    # Fictitious(game),
    AdaptiveAspiration(game),
    Enforcer(game),
    ZDExtortion(game),
    LOLA(game),
)

championship = Championship(
    players=players,
    max_rounds=400,
    stop_prob=0.01,
    error=0.01,
    repetitions=2,
    generations=10,
    initial_population=len(players)*3,
)
print("Starting Championship...")
df1, df2, df3 = championship.play(return_dfs=True)
print("Saving results...")

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


df1.to_parquet(f"{output_folder}/{timestamp}_first_phase.parquet", index=False)
df2.to_parquet(f"{output_folder}/{timestamp}_second_phase.parquet", index=False)
df3.to_parquet(f"{output_folder}/{timestamp}_third_phase.parquet", index=False)