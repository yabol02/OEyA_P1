"""
limited_sum
===========

A Python package implementing an iterative limited-sum game framework.

This package provides the following main components:

- :class `Game`: Defines the payoff structure and game logic.
- :class `Player`: Abstract base class for all player strategies.
- :class `Match`: Simulates a repeated game between two players.
- :class `Tournament`: Runs multiple matches among different players.
- :class `Evolution`: Models evolutionary dynamics among strategies.
- :class `Championship`: Organizes a 3 phases championship (tournament and 2 evolutions) among players.
"""

from .championship import Championship
from .chosen_player import HatTricker
from .evolution import Evolution, ProportionalEvolution
from .game import ACTIONS, THRESHOLD, Game
from .match import Match
from .player import (LOLA, WSLS, AdaptiveAspiration, AdaptivePavlov, Always0,
                     Always3, BinarySunset, CastigadorInfernal, CleverAgent,
                     ContriteTitForTat, CopyCat, Detective,
                     DeterministicSimpletron, Enforcer, Fictitious,
                     FictitiousSoftmax, Focal5, GenerousTitForTat, GreedyBayes,
                     GrimTrigger, PermissiveTitForTat, Player, Random23,
                     RegretMatching, StrongAWSLS, TitForTat, UniformRandom,
                     WeightedRandom23, ZDExtortion)
from .tournament import Tournament

__all__ = [
    "ACTIONS",
    "THRESHOLD",
    "Game",
    "Player",
    "Always0",
    "Always3",
    "UniformRandom",
    "Focal5",
    "TitForTat",
    "CastigadorInfernal",
    "Match",
    "Tournament",
    "Evolution",
    "DeterministicSimpletron",
    "PermissiveTitForTat",
    "create_agent",
    "AGENT_CLASSES",
    "Detective",
    "AdaptivePavlov",
    "ContriteTitForTat",
    "GenerousTitForTat",
    "GrimTrigger",
    "HatTricker",
    "Random23",
    "WeightedRandom23",
    "CleverAgent",
    "WSLS",
    "StrongAWSLS",
    "BinarySunset",
    "CopyCat",
    "ProportionalEvolution",
    "Championship",
    "build_several_agents",
    "FictitiousSoftmax",
    "RegretMatching",
    "GreedyBayes",
    "Fictitious",
    "AdaptiveAspiration",
    "Enforcer",
    "ZDExtortion",
    "LOLA",
]
