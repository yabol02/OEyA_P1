"""
limited_sum
===========

A Python package implementing an iterative limited-sum game framework.

This package provides the following main components:

- :class:`Game`: Defines the payoff structure and game logic.
- :class:`Player`: Abstract base class for all player strategies.
- :class:`Match`: Simulates a repeated game between two players.
- :class:`Tournament`: Runs multiple matches among different players.
- :class:`Evolution`: Models evolutionary dynamics among strategies.
"""

from .game import Game, ACTIONS, THRESHOLD
from .player_builder import create_agent, AGENT_CLASSES, build_several_agents
from .player import (
    Player,
    Always0,
    Always3,
    UniformRandom,
    Focal5,
    TitForTat,
    CastigadorInfernal,
    Deterministic_simpletron,
    PermissiveTitForTat,
    Detective, AdaptivePavlov,
    ContriteTitForTat, GenerousTitForTat, 
    GrimTrigger, 
)
from .match import Match
from .tournament import Tournament
from .evolution import Evolution

__all__ = [
    "Game",
    "Player",
    "Always0",
    "Always3",
    "UniformRandom",
    "Focal5",
    "TitForTat",
    "CastigadorInfernal",
    "Deterministic_simpletron",
    "PermissiveTitForTat",
    "Match",
    "Tournament",
    "Evolution",
    "create_agent",
    "AGENT_CLASSES",
    "Detective",
    "AdaptivePavlov",
    "ContriteTitForTat",
    "GenerousTitForTat",
    "GrimTrigger",
    "build_several_agents"
]
