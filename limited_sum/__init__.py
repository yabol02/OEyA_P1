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
"""

from .championship import Championship
from .evolution import Evolution
from .game import ACTIONS, THRESHOLD, Game
from .match import Match
from .player import (AWSLS, AdaptivePavlov, AgenteAstuto, Always0, Always3,
                     BinarySunset, CastigadorInfernal, ContriteTitForTat,
                     CopyCat, Detective, DeterministicSimpletron,
                     FictitiousSoftmax, Focal5, GenerousTitForTat, GrimTrigger,
                     HatTricker, PermissiveTitForTat, Player, Random23,
                     RegretMatching, TitForTat, UniformRandom,
                     WeightedRandom23, WSLS_Adapted)
from .player_builder import AGENT_CLASSES, build_several_agents, create_agent
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
    "AgenteAstuto",
    "WSLS_Adapted",
    "AWSLS",
    "BinarySunset",
    "CopyCat",
    "Championship",
    "build_several_agents",
    "FictitiousSoftmax",
    "RegretMatching",
]
