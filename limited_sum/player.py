from abc import ABC, abstractmethod
from collections import Counter
from math import exp, inf
from random import choice, choices, random
from typing import Self

from .game import Game


# Base class for all player strategies
class Player(ABC):
    """
    Abstract base class representing a generic player in a limited-sum game.

    Each player maintains a history of their past actions and must implement
    a strategy for deciding the next move given the opponent's behavior.
    """

    @abstractmethod
    def __init__(self, game: Game, name: str = ""):
        """
        Initializes a player instance.

        :param game: The game that this player will participate in.
        :type game: Game
        :param name: The name of the strategy.
        :type name: str
        """
        self.name = name
        self.game = game
        self.history = list()

    @abstractmethod
    def strategy(self, opponent: Self) -> int:
        """
        Defines the strategy used by the player to select an action.

        This method must be implemented by all subclasses and returns the action chosen by the player
        for the next round, possibly based on the opponent's history.

        :param opponent: Another instance of ``Player`` representing the opponent.
        :type opponent: Player
        :return: An integer representing the chosen action (0 to 5).
        :rtype: int
        """
        pass

    def compute_scores(self, opponent: Self) -> tuple[float, float]:
        """
        Computes the payoffs for the current player and an opponent.

        :param opponent: Another instance of ``Player`` representing the opponent.
        :type opponent: Player
        :return: A tuple containing two floats: the current player's payoff and the opponent's payoff.
        :rtype: tuple[float, float]
        """
        if len(self.history) != len(opponent.history):
            raise ValueError("Histories must be of the same length to compute scores.")

        player_score = 0.0
        opponent_score = 0.0

        for p1_action, p2_action in zip(self.history, opponent.history):
            p1_payoff, p2_payoff = self.game.evaluate_result(p1_action, p2_action)
            player_score += p1_payoff
            opponent_score += p2_payoff

        return player_score, opponent_score

    def clean_history(self) -> None:
        """
        Resets the history of the current player.

        :return: None
        :rtype: None
        """
        self.history = []

    def _get_last_payoff(self, opponent):
        my_last_action = self.history[-1]
        last_opp_action = opponent.history[-1]
        return self.game.evaluate_result(my_last_action, last_opp_action)[0]

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        history_len = len(self.history)
        return f"{class_name}(name={self.name!r}, history_len={history_len})"

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{self.name} ({class_name})"


# Basic strategy implementations
class Always0(Player):
    """
    Strategy that always selects action 0.
    """

    def __init__(self, game: Game, name: str = "Always 0"):
        """
        Initializes the Always0 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Always0, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 0 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 0.
        :rtype: int
        """
        return 0


class Always3(Player):
    """
    Strategy that always selects action 3.
    """

    def __init__(self, game: Game, name: str = "Always 3"):
        """
        Initializes the Always3 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Always3, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Always returns 3 as the chosen action.

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: Always 3.
        :rtype: int
        """
        return 3


class UniformRandom(Player):
    """
    Strategy that chooses an action uniformly at
    """

    def __init__(self, game: Game, name: str = "Uniform Random"):
        """
        Initializes the UniformRandom player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(UniformRandom, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Chooses an action uniformly at

        :param opponent: The opposing player (unused in this strategy).
        :type opponent: Player
        :return: A random integer between 0 and 5.
        :rtype: int
        """
        return choice(self.game.actions)


class Focal5(Player):
    """
    Strategy that tries to coordinate so that i + j = 5 in each round.
    Several possible implementations exist.
    """

    COORDINATION_ACTION = 3

    def __init__(self, game: Game, name: str = "Focal 5"):
        """
        Initializes the Focal5 player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(Focal5, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Attempts to coordinate on i + j = 5.

        In the first round, it plays COORDINATION_ACTION (3). In subsequent rounds, it adapts
        based on the opponent's last move to maximize the chances of maintaining the efficient sum of 5.

        - If the opponent played a_opp, the target action is 5 - a_opp.
        - The chosen action is clipped to be between 0 and 5.

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        if not opponent.history:
            return self.COORDINATION_ACTION

        last_opponent_action = opponent.history[-1]
        desired_action = self.game.threshold - last_opponent_action
        action = max(0, min(self.game.threshold, desired_action))

        return action


class TitForTat(Player):
    """
    Reactive strategy inspired by the classic Tit-for-Tat, adapted for the limited-sum game.
    """

    COOPERATIVE_ACTION = 2

    def __init__(self, game: Game, name: str = "Tit for Tat"):
        """
        Initializes the TitForTat player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super(TitForTat, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Reacts to the opponent's past actions, rewarding cooperation and punishing greedy behavior (actions above 3).

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        if not opponent.history:
            return self.COOPERATIVE_ACTION

        last_opponent_action = opponent.history[-1]

        return last_opponent_action


class CastigadorInfernal(Player):
    """
    Adaptive strategy for the limited-sum game that balances coordination and self-protection.

    Strategy logic:
        - Starts trying to coordinate on i + j = 5 (efficient outcome).
        - Monitors opponent’s cooperation patterns and adapts accordingly.
        - Uses graduated punishment for greedy behavior.
        - Attempts forgiveness and cooperation recovery.
        - Adjusts strategy based on opponent’s consistency.
    """

    def __init__(self, game: Game, name: str = "Castigador Infernal"):
        """
        Initializes the CastigadorInfernal player.

        :param game: The game being played.
        :type game: Game
        :param name: Optional name of the strategy.
        :type name: str
        """
        super().__init__(game, name)
        self.cooperation_score = 0  # Tracks opponent's cooperative behavior.
        self.punishment_mode = False
        self.punishment_rounds = 0

    def strategy(self, opponent: Player) -> int:
        """
        Determines the next action based on adaptive cooperation tracking.

        The strategy combines cooperation attempts, punishment for exploitation, and recovery after punishment periods.

        :param opponent: The opposing player.
        :type opponent: Player
        :return: The chosen action (0 to 5).
        :rtype: int
        """
        # First round: start with 2 (middle ground)
        if not self.history:
            return 2

        last_opponent = opponent.history[-1]

        # Update cooperation tracking
        if last_opponent <= 3:
            self.cooperation_score += 1
        else:
            self.cooperation_score -= 2

        # Analyze opponent's recent behavior
        recent_rounds = min(5, len(opponent.history))
        recent_actions = opponent.history[-recent_rounds:]
        avg_recent = sum(recent_actions) / len(recent_actions)

        # Punishment phase
        if self.punishment_mode:
            self.punishment_rounds += 1
            if self.punishment_rounds <= 2:
                return last_opponent  # Vamos a hacer que el castigo sea Tic of Tat
            else:
                self.punishment_mode = False
                self.punishment_rounds = 0
                return 2

        # Detect consistent greedy behavior
        if last_opponent > 3 and avg_recent > 3.5:
            self.punishment_mode = True
            self.punishment_rounds = 0
            return last_opponent  # Vamos a hacer que el castigo sea Tic of Tat

        # Normal coordination attempt
        if last_opponent <= 3:
            return max(0, min(5, 5 - last_opponent))

        # Default fallback
        return 2


# Basic but "intelligent" implementations
class DeterministicSimpletron(Player):
    """
    Starts cooperating (return 2) if the player cooperates it returns the same value.
    If the oponent does not cooperate, it switches the strategy from cooperating to being greedy (return 3) or from being greedy to cooperating
    """

    def __init__(
        self,
        game: Game,
        name: str = "Deterministic Simpletron",
        pesimist_start: bool = False,
        tit_for_tat_punishment: bool = False,
    ):
        # Basic initialization of the agent
        super(DeterministicSimpletron, self).__init__(game, name)

        # Configuration parameters
        self.pesimist_start = pesimist_start
        self.tit_for_tat_punishmnet = tit_for_tat_punishment

        # Internal flag to know if the agent is in "punishment" mode (True = apply punishment; False = normal behavior)
        self.do_punish = False

    def strategy(self, opponent: Player) -> int:
        if len(self.history) == 0:
            if self.pesimist_start:
                return 3
            else:
                return 2

        # Check if the opponent is greedy
        last_opponent_action = opponent.history[-1]
        if last_opponent_action >= 3:
            # The opponent is greedy, switch mode
            self.do_punish = not (self.do_punish)

        if self.do_punish:
            if self.tit_for_tat_punishmnet:
                return last_opponent_action
            else:
                return 3
        else:
            return self.history[-1]


class PermissiveTitForTat(Player):
    """
    Permissive Tit-for-Tat strategy with a 'patience' attribute.
    Patience decreases if the opponent chooses an action >= 3 and resets if they choose an action < 3.
    """

    INITIAL_ACTION = 3
    COOPERATIVE_ACTION = 2
    INITIAL_PATIENCE = 3

    def __init__(
        self,
        game: Game,
        name: str = "Permissive Tit for Tat",
        initial_patience: int = 3,
    ):
        super(PermissiveTitForTat, self).__init__(game, name)
        self.patience = initial_patience
        self.INITIAL_PATIENCE = initial_patience

    def strategy(self, opponent: Player) -> int:
        if not opponent.history:
            # If no history, start with the cooperative action
            return self.INITIAL_ACTION

        last_opponent_action = opponent.history[-1]

        # Patience adjustment logic

        if last_opponent_action >= 3:
            # If the opponent is 'greedy' (chooses 3 or more), decrease patience
            self.patience = max(0, self.patience - 1)
        elif last_opponent_action < 3:
            # If the opponent chooses less than 3, reset patience
            self.patience = self.INITIAL_PATIENCE

        # Action logic
        if self.patience == 0:
            return last_opponent_action
        else:
            return self.COOPERATIVE_ACTION


class GrimTrigger(Player):
    """
    Grim Trigger strategy: Cooperate until the opponent defects once, then punish forever.
    """

    COOPERATIVE_ACTION = 2
    PUNISHMENT_ACTION = 3  # The most mild defection

    def __init__(self, game: Game, name: str = "Grim Trigger"):
        super(GrimTrigger, self).__init__(game, name)
        self.triggered = False  # Punishment state

    def strategy(self, opponent: Player) -> int:
        # If already in punishment mode, punish forever.
        if self.triggered:
            return self.PUNISHMENT_ACTION

        # Check the opponent's history for any past defections
        if not opponent.history:
            return self.COOPERATIVE_ACTION  # Cooperate in the first round

        # If the opponent defected in the last round (or any previous round)
        if opponent.history[-1] > self.COOPERATIVE_ACTION:
            self.triggered = True
            return self.PUNISHMENT_ACTION

        # If no betrayal, continue cooperating
        return self.COOPERATIVE_ACTION


class GenerousTitForTat(Player):
    """
    Generous Tit-for-Tat (GTFT) strategy.

    Follows the logic of TFT (cooperate if the opponent cooperated, punish if they defected),
    but with a probability 'generosity_prob', forgives an opponent's defection and cooperates anyway.
    This is crucial to break mutual punishment cycles initiated by an error (noise).
    """

    def __init__(
        self,
        game: Game,
        name: str = "Generous TFT",
        accion_cooperativa: int = 2,
        accion_castigo: int = 3,
        prob_generosidad: float = 0.1,
    ):

        super(GenerousTitForTat, self).__init__(game, name)
        self.COOPERATIVE_ACTION = accion_cooperativa
        self.PUNISHMENT_ACTION = accion_castigo
        self.GENEROSITY_PROB = prob_generosidad

    def strategy(self, opponent: Player) -> int:
        # Cooperate in the first round
        if not opponent.history:
            return self.COOPERATIVE_ACTION

        last_opponent_action = opponent.history[-1]

        # 1. If the opponent cooperated, we cooperate
        if last_opponent_action <= self.COOPERATIVE_ACTION:
            return self.COOPERATIVE_ACTION

        # 2. If the opponent defected...
        else:
            # 3. Decide whether to be generous (forgive) or punish
            if random() < self.GENEROSITY_PROB:
                # Forgiveness: Break the cycle by cooperating
                return self.COOPERATIVE_ACTION
            else:
                # Punishment: Follow the TFT rule
                return self.PUNISHMENT_ACTION


class ContriteTitForTat(Player):
    """
    A contrite (arrepentido en español) Tit-for-Tat.
    This strategy focuses on the *other* side of noise: What if *I* caused the problem?
    1. If the last round was a success (Payoff > 0), play like TFT.
    2. If the last round was a failure (Payoff = 0), take the blame (be contrite) and cooperate, hoping this breaks the punishment cycle.
    """

    def __init__(
        self,
        game: Game,
        name: str = "Contrite TFT",
        accion_cooperativa: int = 2,
        accion_castigo: int = 3,
    ):

        super(ContriteTitForTat, self).__init__(game, name)
        self.COOPERATIVE_ACTION = accion_cooperativa
        self.PUNISHMENT_ACTION = accion_castigo

    def strategy(self, opponent: Player) -> int:
        # Cooperate in the first round
        if not self.history:
            return self.COOPERATIVE_ACTION

        my_last_payoff = self._get_last_payoff(opponent)

        # 1. Contrition: If the result was 0, cooperate to fix it.
        if my_last_payoff == 0:
            return self.COOPERATIVE_ACTION

        # 2. Success: If the payoff was > 0, play like standard TFT.
        else:
            last_opponent_action = opponent.history[-1]
            if last_opponent_action > self.COOPERATIVE_ACTION:
                return self.PUNISHMENT_ACTION
            else:
                return self.COOPERATIVE_ACTION


class Detective(Player):
    """
    Estrategia "Detective" (Sondeador) mejorada.

    Capaz de clasificar oponentes como:
    - ALWAYS_0, ALWAYS_3
    - ALL_COOP (Always 2)
    - ALL_DEFECT (Always 3 o más)
    - TIT_FOR_TAT (Copia mi acción anterior)
    - FOCAL_5 (Juega 5 - mi_accion_anterior)
    - RANDOM (Muestra alta variabilidad)
    - REACTIVE_GTFT (Similar a TFT, pero con posible perdón)
    - UNKNOWN (Si no se ajusta a ningún patrón conocido)
    """

    def __init__(
        self,
        game: Game,
        name: str = "Detective Avanzado",
        accion_cooperativa: int = 2,
        accion_castigo: int = 3,
        secuencia_sondeo: list[int] = [2, 3, 0, 5],
        fallback_strategy: str = "TFT",
    ):

        super(Detective, self).__init__(game, name)
        self.COOP_ACTION = accion_cooperativa
        self.PUNISH_ACTION = accion_castigo
        self.PROBE_SEQUENCE = secuencia_sondeo
        self.FALLBACK_STRATEGY = fallback_strategy

        self.probe_len = len(self.PROBE_SEQUENCE)
        self.analysis_done = False
        self.opponent_type = "UNKNOWN"

    def _analyze_opponent(self, opponent: Player):
        """Método interno para clasificar al oponente después del sondeo."""
        self.analysis_done = True
        op_history = opponent.history[: self.probe_len]
        my_probes = self.PROBE_SEQUENCE

        # La acción inicial del Detective debe ser considerada como la acción
        # a la que reacciona el oponente en la ronda 1.
        # En este caso, mi acción en la ronda n reacciona a la acción del oponente en n-1.
        # Por simplicidad, consideraremos la secuencia de acciones del oponente.

        # --- 1. Clasificación de Estrategias Fijas (Siempre Juega X) ---
        if all(v == 0 for v in op_history):
            self.opponent_type = "ALWAYS_0"
            return
        if all(v == self.PUNISH_ACTION for v in op_history):
            self.opponent_type = "ALWAYS_3"
            return
        if all(v == 2 for v in op_history):
            self.opponent_type = (
                "ALL_COOP"  # Podría ser TFT si la secuencia empieza con 2
            )
            return
        if all(v == 5 for v in op_history):
            self.opponent_type = "ALWAYS_5"
            return

        # --- 2. Clasificación de Estrategias Reactivas ---

        # Tit For Tat (TFT) o PermissiveTFT (si la paciencia se agota pronto)
        # Reacción esperada: la acción del oponente en n es igual a mi acción en n-1.
        # Asumiendo que yo empiezo con PROBE_SEQUENCE[0] y el oponente reacciona a mi
        # acción previa (o coopera inicialmente si es TFT).
        # Sequencia de oponente TFT: [2 (coop inicial), 2, 3, 0, ...]
        expected_tft_response = [self.COOP_ACTION] + my_probes[:-1]

        # Nota: Usaremos sólo las primeras `probe_len - 1` rondas para la comparación
        # o asumimos una acción inicial de cooperación para el oponente.
        if (
            op_history[1:] == my_probes[:-1]
        ):  # El oponente copió todas mis acciones menos la primera
            self.opponent_type = "TIT_FOR_TAT"
            return

        # Focal 5 (Coordina en suma 5: 5 - mi_accion)
        # Mi acción: [a0, a1, a2, a3]
        # Su acción (Focal 5): [5-a0, 5-a1, 5-a2, 5-a3]
        # Usamos la acción del oponente en n para ver si intentó sumar 5 con mi acción en n-1.
        # Es más simple ver si op[i] + mi[i] = 5
        focal_5 = True
        for i in range(self.probe_len - 1):
            # Comprueba si op[i+1] (su jugada en R2, R3, R4)
            # + mi[i] (mi jugada en R1, R2, R3) == 5

            if op_history[i + 1] + my_probes[i] != self.game.threshold:
                focal_5 = False
                break
        if focal_5:
            self.opponent_type = "FOCAL_5"
            return

        # --- 3. Clasificación de Estrategias de Patrón ---

        # Uniform Random
        # La varianza de las acciones será alta. Si la desviación estándar es > 1.5,
        # es un buen indicador de aleatoriedad.
        avg_op = sum(op_history) / self.probe_len
        variance = sum([(x - avg_op) ** 2 for x in op_history]) / self.probe_len
        if variance > 1.5 and len(set(op_history)) > 2:
            self.opponent_type = "RANDOM"
            return

        # Grim Trigger / Castigador Infernal / Deterministic Simpletron (Modo Castigo)
        # Si el oponente juega inicialmente con 2 y luego siempre juega 3 después de mi deserción (mi acción 3)
        # Es difícil diferenciar sin más rondas o sin una historia de pagos.
        # Nos enfocamos en la deserción permanente.
        if (
            op_history[0] == 2
            and op_history[1] == 3
            and all(v == 3 for v in op_history[2:])
        ):
            self.opponent_type = "GRIM_TRIGGER_LIKE"
            return

        # Si no se ajusta a ningún patrón, se queda como 'UNKNOWN'.

    def strategy(self, opponent: Player) -> int:
        round_num = len(self.history)

        # Fase 1: Sondeo
        if round_num < self.probe_len:
            return self.PROBE_SEQUENCE[round_num]

        # Fase 2: Análisis (solo se ejecuta una vez)
        if not self.analysis_done:
            # Asumo que self.game.threshold existe (usualmente 5 en este contexto)
            self._analyze_opponent(opponent)

        # Fase 3: Estrategia post-análisis

        last_opponent_action = opponent.history[-1]

        if self.opponent_type == "ALWAYS_0":
            # Jugar 5 para obtener el máximo beneficio (5 + 0 = 5)
            return self.game.threshold

        elif (
            self.opponent_type == "ALWAYS_3"
            or self.opponent_type == "GRIM_TRIGGER_LIKE"
        ):
            # Ellos siempre jugarán 3. Jugar  3 o + resulta en Pago=0.
            # No queremos recompensar esta estrategia ni queremos ganar 0
            # asi que jugamos aleatoriamente entre 2 y 3
            return choice([self.COOP_ACTION, self.PUNISH_ACTION])

        elif self.opponent_type == "ALL_COOP" or self.opponent_type == "ALWAYS_2":
            # Explotar: jugar 3 para obtener (3 + 2 = 5), Pago = 3.
            return self.PUNISH_ACTION

        elif self.opponent_type == "ALWAYS_5":
            # Ellos juegan 5, yo juego 0 (5+0=5), Pago=0. No hay beneficio.
            return self.PUNISH_ACTION

        elif self.opponent_type == "TIT_FOR_TAT":
            # Jugar TFT contra TFT (es la mejor respuesta para la cooperación mutua)
            # Replicar su última acción.
            return last_opponent_action

        elif self.opponent_type == "FOCAL_5":
            # Mantener la coordinación óptima.
            desired_action = self.game.threshold - last_opponent_action
            return max(0, min(self.game.threshold, desired_action))

        elif self.opponent_type == "RANDOM":
            # Adoptar una estrategia robusta y segura, como la cooperación.
            return self.COOP_ACTION

        # --- Estrategia de Retorno (Fallback) ---
        else:
            # UNKNOWN o patrones difíciles (e.g., Castigador Infernal, GTFT)
            # Volver a una estrategia robusta preconfigurada (TFT o GTFT)
            if self.FALLBACK_STRATEGY == "TFT":
                # TFT simple
                return last_opponent_action
            else:
                # Por defecto, cooperar
                return self.COOP_ACTION


class Random23(Player):
    """
    Player that randomly chooses between 2 and 3.
    """

    def __init__(self, game: Game, name: str = "Random 2 or 3"):
        super(Random23, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        return choice([2, 3])


class WeightedRandom23(Player):
    """
    Player that chooses between 2, 3, and 4 with weighted probabilities.
    """

    def __init__(
        self, game: Game, name: str = "Weighted Random 2, 3, or 4", w=[0.75, 0.25]
    ):
        super(WeightedRandom23, self).__init__(game, name)
        self.w = w
        assert len(w) == 2, "Weights list must have exactly two elements."
        assert sum(w) == 1.0, "Weights must sum to 1.0."

    def strategy(self, opponent: Player) -> int:
        return choices([2, 3], weights=self.w)[0]


class BinarySunset(Player):
    """
    A player that only plays binary numbers (2, 4) and that starts more agressive (4) until the sunset where it collaborates (2).
    """

    def __init__(self, game: Game, name: str = "BinarySunset"):
        super(BinarySunset, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        num_plays = len(opponent.history)
        play = 2
        if num_plays <= 20:
            play = 4
        elif num_plays <= 50:
            if num_plays % 2 == 0:
                play = 4

        return play


# Advanced "Intelligent" implementations
class CleverAgent(Player):
    """
    A clever and adaptive strategy that seeks balance between cooperation, exploitation, and punishment.
    It bases its logic on heuristics to maximize its score while avoiding long-term retaliation.

    Strategy logic:
    1.  **Priority 1 (Defense):** If the opponent is greedy (plays >= 3), punish by playing 3 to ensure a (0, 0) outcome.
    2.  **Priority 2 (Safety):** If we just exploited (played 3 or 4 in the previous round) and the opponent is *not* greedy,
        we should cooperate (play 2) to avoid patterns and "reset" the patience of "Permissive Tit-for-Tat" type opponents.
    3.  **Priority 3 (Exploitation):** If the opponent cooperates (< 3) and we have not just exploited:
        -   If they play 1: We play 4 (maximum exploitation).
        -   If they play 0 or 2: With a probability (exploitation_prob), we play 3 to gain extra points.
    4.  **Priority 4 (Cooperation):** If none of the exploitation conditions are met, cooperate by playing 2.
    5.  **Priority 5 (Never Play 5):** This strategy never plays action 5.
    """

    COOP_ACTION = 2
    EXPLOIT_ACTION = 3
    PUNISH_ACTION = 3
    MAX_EXPLOIT_ACTION = 4

    def __init__(
        self, game: Game, name: str = "Clever Agent", exploitation_prob: float = 0.20
    ):
        super(CleverAgent, self).__init__(game, name)

        self.just_exploited = False
        self.EXPLOITATION_PROB = exploitation_prob

    def strategy(self, opponent: Player) -> int:

        if not self.history:
            self.just_exploited = False
            return self.COOP_ACTION

        last_opponent_action = opponent.history[-1]
        my_action = 0

        # --- PRIORITY 1: DEFENSE (Anti-Greed Rule) ---
        if last_opponent_action >= 3:
            my_action = self.PUNISH_ACTION
            self.just_exploited = True
            return my_action

        # --- PRIORITY 2: SAFETY (Never Twice Rule) ---
        if self.just_exploited:
            my_action = self.COOP_ACTION
            self.just_exploited = False  # Reset our state
            return my_action

        # --- PRIORITY 3: EXPLOITATION (Opportunism) ---
        if last_opponent_action == 1:
            my_action = self.MAX_EXPLOIT_ACTION
            self.just_exploited = True
            return my_action

        if last_opponent_action in [0, 2]:
            if random() < self.EXPLOITATION_PROB:
                my_action = self.EXPLOIT_ACTION
                self.just_exploited = True
                return my_action
            else:
                my_action = self.COOP_ACTION
                self.just_exploited = False
                return my_action

        # --- PRIORITY 4: COOPERATION (Fallback) ---
        my_action = self.COOP_ACTION
        self.just_exploited = False
        return my_action


class WSLS(Player):
    """
    Basic Win-Stay Lose-Shift adapted to 0..5 with aspiration
    """

    def __init__(self, game, aspiration=2.5, name="WSLS"):
        super().__init__(game, name)
        self.aspiration = aspiration

    def strategy(self, opponent):
        if not self.history:
            return 2
        last_payoff = self._get_last_payoff(opponent)
        last_action = self.history[-1]
        if last_payoff >= self.aspiration:
            # Stay: repeat last action
            return last_action
        else:
            # Shift: try to adjust to avoid collapse
            if last_action + opponent.history[-1] > self.game.threshold:
                return max(0, last_action - 1)
            # If the failure was due to sum>max -> decrease
            else:
                return min(5, last_action + 1)


class StrongAWSLS(Player):
    """
    Improved Adaptive Win-Stay Lose-Shift (AWSLS) strategy.
    """

    def __init__(
        self,
        game,
        A=2.5,
        delta=1,
        forgive_prob=0.1,
        punish_len=2,
        a0=2,
        name="Strong AWSLS",
    ):
        super().__init__(game, name)
        self.A = A
        self.delta = delta
        self.f = forgive_prob
        self.k = punish_len
        self.a0 = a0
        self._punish_timer = 0

    def strategy(self, opponent):
        if not self.history:
            return self.a0

        # Punishment phase
        if self._punish_timer > 0:
            return 0

        last_payoff = self._get_last_payoff(opponent)
        my_last = self.history[-1]
        opp_last = opponent.history[-1]

        # If last payoff was satisfactory, stay (with possibility to explore/forgive)
        if last_payoff >= self.A:
            # Small forgiveness: with probability f, try to increase (take advantage of cooperators)
            if random() < self.f:
                return min(5, my_last + self.delta)
            return my_last

        # Collapse case (sum>max): decrease
        if my_last + opp_last > self.game.threshold:
            recent = (
                opponent.history[-3:]
                if len(opponent.history) >= 3
                else opponent.history
            )
            if (
                all(o > (self.game.threshold - my_last) for o in recent)
                and len(recent) >= 2
            ):
                self._punish_timer = self.k
                return 0
            return max(0, my_last - self.delta)

        # If the opponent contributed little -> try to increase to capture more
        if opp_last <= 2:
            return min(5, my_last + self.delta)

        # In other cases, decrease to avoid collapses
        return max(0, my_last - self.delta)


class AdaptivePavlov(Player):
    """
    Adaptive Pavlov Strategy (it uses the idea behind WSLS).
    The simple "Pavlov" strategy alternates between two actions.
    This version allows more flexibility in the "Lose-Shift" logic.
    """

    def __init__(
        self,
        game: Game,
        name: str = "Adaptive Pavlov",
        accion_cooperativa: int = 2,
        accion_desercion: int = 3,
        shift_strategy: str = "toggle",
    ):
        """
        :param accion_cooperativa: Acción base de cooperación (default: 2).
        :param accion_desercion: Acción base de deserción (default: 3).
        :param shift_strategy: Cómo "cambiar" al perder (Pago=0).
                               'toggle': Alterna entre accion_cooperativa y accion_desercion.
                               'random': Elige aleatoriamente entre las dos.
                               'always_coop': Siempre cambia a accion_cooperativa.
        """
        super(AdaptivePavlov, self).__init__(game, name)
        self.COOP_ACTION = accion_cooperativa
        self.DEFECT_ACTION = accion_desercion
        self.SHIFT_STRATEGY = shift_strategy

    def strategy(self, opponent: Player) -> int:
        if not self.history:
            return self.COOP_ACTION

        my_last_payoff = self._get_last_payoff(opponent)
        my_last_action = self.history[-1]

        # 1. WIN-STAY (Ganar-Quedarse)
        if my_last_payoff > 0:
            return my_last_action

        # 2. LOSE-SHIFT (Perder-Cambiar)
        else:
            if self.SHIFT_STRATEGY == "toggle":
                return (
                    self.DEFECT_ACTION
                    if my_last_action == self.COOP_ACTION
                    else self.COOP_ACTION
                )

            elif self.SHIFT_STRATEGY == "random":
                return choice([self.COOP_ACTION, self.DEFECT_ACTION])

            elif self.SHIFT_STRATEGY == "always_coop":
                return self.COOP_ACTION

            else:  # Default a 'toggle'
                return (
                    self.DEFECT_ACTION
                    if my_last_action == self.COOP_ACTION
                    else self.COOP_ACTION
                )


class CopyCat(Player):
    """
    Childish player that copies the opponent's last move.
    """

    def __init__(self, game: Game, name: str = "CopyCat"):
        super(CopyCat, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        if not opponent.history:
            return 2
        return opponent.history[-1]


class Fictitious(Player):
    """
    Assumes the opponent plays according to a stationary probability distribution based on their historical frequency.
    It chooses the best response to that distribution.
    """

    def __init__(self, game, name="Fictitious"):
        super().__init__(game, name)

    def strategy(self, opponent: Self) -> int:
        if not opponent.history:
            return choice([2, 3])

        opp_history = opponent.history
        total_rounds = len(opp_history)
        counts = Counter(opp_history)

        best_action = 0
        max_ev = -1.0

        for my_act in self.game.actions:
            ev = 0.0
            for opp_act, count in counts.items():
                prob = count / total_rounds
                payoff, _ = self.game.evaluate_result(my_act, opp_act)
                ev += prob * payoff

            if ev > max_ev:
                max_ev = ev
                best_action = my_act
            elif ev == max_ev:
                if random() < 0.5:
                    best_action = my_act

        return best_action


class FictitiousSoftmax(Player):
    """
    Fictitious Player with softmax action selection.

    The agent keeps an empirical distribution of opponent actions.
    Expected payoffs are computed and a softmax over them determines the probability of choosing each action.
    """

    def __init__(self, game, tau: float = 0.5, name: str = "FictitiousSoftmax"):
        super().__init__(game, name)
        self.tau = tau

    def _estimate_frequencies(self, opponent):
        counts = {a: 0 for a in self.game.actions}
        if opponent.history:
            for act in opponent.history:
                counts[act] += 1
            total = len(opponent.history)
            return {a: counts[a] / total for a in self.game.actions}
        else:
            # Uniform prior when no information
            return {a: 1 / len(self.game.actions) for a in self.game.actions}

    def _softmax(self, values):
        max_v = max(values)
        exps = [exp((v - max_v) / self.tau) for v in values]
        Z = sum(exps)
        return [x / Z for x in exps]

    def strategy(self, opponent):
        freqs = self._estimate_frequencies(opponent)

        # Compute expected payoff for each i
        expected_values = []
        for i in self.game.actions:
            ev = 0.0
            for j, pj in freqs.items():
                pay_i, _ = self.game.evaluate_result(i, j)
                ev += pj * pay_i
            expected_values.append(ev)

        # Softmax over expected values
        probs = self._softmax(expected_values)
        return choices(self.game.actions, weights=probs, k=1)[0]


class RegretMatching(Player):
    """
    Tracks cumulative regrets for not having played each action in the past,
    and chooses next action with probability proportional to positive regrets.
    If all regrets are zero, the agent plays uniformly.
    """

    def __init__(self, game, name: str = "RegretMatching"):
        super().__init__(game, name)
        self.regrets = {a: 0.0 for a in self.game.actions}

    def strategy(self, opponent):
        # First round: play middle action
        if not self.history:
            return 2

        # Update regrets based on last round
        last_action = self.history[-1]
        last_opp = opponent.history[-1]

        # Payoff obtained with actual action
        actual_payoff, _ = self.game.evaluate_result(last_action, last_opp)

        # Update regret for each possible alternative action
        for a in self.game.actions:
            alt_payoff, _ = self.game.evaluate_result(a, last_opp)
            diff = alt_payoff - actual_payoff
            if diff > 0:
                self.regrets[a] += diff

        # Compute probabilities proportional to positive regrets
        positive = {a: max(r, 0) for a, r in self.regrets.items()}
        total = sum(positive.values())

        if total == 0:
            # No regrets → uniform exploration
            return choice(self.game.actions)

        # Weighted random selection
        actions = list(self.game.actions)
        weights = [positive[a] for a in actions]
        return choices(actions, weights=weights, k=1)[0]


class GreedyBayes(Player):
    """
    Bayesian opponent model using a Dirichlet prior over opponent actions.

    - Prior: alpha[a] = 1 for all actions a (uniform uninformative prior)
    - Posterior: alpha[a] += count of opponent playing action a
    - Expected payoff of action i: E[u(i)] = sum_j P(j | posterior) * u(i, j)
    """

    def __init__(self, game, name: str = "GreedyBayes"):
        super().__init__(game, name)
        self.alpha = {a: 1.0 for a in self.game.actions}  # Dirichlet(1,...,1)

    def _posterior_probs(self):
        total = sum(self.alpha.values())
        return {a: self.alpha[a] / total for a in self.game.actions}

    def strategy(self, opponent):
        # Update posterior with last observation
        if opponent.history:
            last_opp = opponent.history[-1]
            self.alpha[last_opp] += 1.0

        # Compute expected payoff for each action
        probs = self._posterior_probs()
        best_value = -inf
        best_actions = []

        for i in self.game.actions:
            ev = 0.0
            for j, pj in probs.items():
                pay_i, _ = self.game.evaluate_result(i, j)
                ev += pj * pay_i
            if ev > best_value:
                best_value = ev
                best_actions = [i]
            elif ev == best_value:
                best_actions.append(i)

        # Break ties uniformly
        return choice(best_actions)


class AdaptiveAspiration(Player):
    """
    We follow the idea behind Karandikar et al. (1998): Satisficing strategy maintaining an aspiration level (alpha).
    If payoff >= alpha, repeat action with high probability.
    If payoff < alpha, explore randomly.
    Alpha updates over time based on experience.
    """

    def __init__(
        self, game, name="Aspirational", learning_rate=0.1, initial_aspiration=3.0
    ):
        super().__init__(game, name)
        self.alpha = initial_aspiration
        self.learning_rate = learning_rate
        self.epsilon_noise = 0.05

    def strategy(self, opponent: Self) -> int:
        if not self.history:
            return 3

        my_last_action = self.history[-1]
        my_last_payoff = self._get_last_payoff(opponent)

        # 1. Update Aspiration Level: alpha(t+1) = (1-h) * alpha(t) + h * payoff(t)
        self.alpha = (1 - self.learning_rate) * self.alpha + (
            self.learning_rate * my_last_payoff
        )

        # 2. Decision Rule
        # If satisfied (Payoff >= Aspiration) -> Stay (with high prob)
        if my_last_payoff >= self.alpha:
            if random() > self.epsilon_noise:
                return my_last_action
            else:
                return choice(self.game.actions)
        # If dissatisfied -> Shift (Explore)
        else:
            return choice(self.game.actions)


class Enforcer(Player):
    """
    Tries to establish a fair equilibrium (2-3).
    If the opponent plays greedy (>3) causing a crash, it enters a punishment mode playing 5 (guaranteeing 0 for opponent) for 'k' rounds.
    """

    def __init__(self, game, name="Enforcer"):
        super().__init__(game, name)
        self.punishment_remaining = 0
        self.punishment_duration = 2  # How many rounds to punish

    def strategy(self, opponent: Self) -> int:
        if not opponent.history:
            return 2  # Start offering a fair-ish deal (assuming they play 2)

        last_opp_action = opponent.history[-1]
        my_last_action = self.history[-1]
        my_last_payoff = self._get_last_payoff(opponent)

        if self.punishment_remaining > 0:
            self.punishment_remaining -= 1
            return 5  # Nobody earns anything.

        # Analyze last round: If we crashed (payoff 0) AND it was because they were greedy (they asked > 2)
        if my_last_payoff == 0 and last_opp_action >= 3:
            self.punishment_remaining = self.punishment_duration
            return 5

        # If they are very passive (playing 0 or 1), take advantage slightly but safely
        if last_opp_action <= 1:
            return 4

        # Standard cooperation: Try to hit the sum 5.
        if last_opp_action == 2:
            return 3
        elif last_opp_action == 3:
            return 2

        return 2


class ZDExtortion(Player):
    """
    We follow the idea behind Press & Dyson (2012), where P_me = chi * P_opponent.
    Implements a ZD strategy that enforces a linear relationship where the agent earns more than the opponent (Extortion).
    If the ratio of scores isn't favorable, it defects (plays 5) to lower opponent score.
    """

    def __init__(self, game, name="ZD Extortion", chi=1.2):
        super().__init__(game, name)
        self.chi = chi  # Extortion factor (I want to earn chi times what you earn)

    def strategy(self, opponent: Self) -> int:
        if not self.history:
            return 2

        my_score, opp_score = self.compute_scores(opponent)

        if opp_score == 0:
            opp_score = 0.1

        current_ratio = my_score / opp_score

        if current_ratio >= self.chi:
            # I am winning by enough, so I play optimally to maximize absolute score
            return 2  # Greedy but possible
        else:
            # I am losing relative ground, so I punish my opponent.
            return 5


class LOLA(Player):
    """
    We follow the idea behind J. Foerster, et al. (2018): Simplified Learning with Opponent-Learning Awareness.
    It simulates: "If I play X, how will the opponent update their move next turn?"
    Assumes opponent is a Naive learner (e.g., repeats if win, lowers if crash).
    Since this is a simple tournament, we simplify: Best Response against their PREDICTED move.
    """

    def __init__(self, game, name="LOLA"):
        super().__init__(game, name)

    def _predict_opponent_next(
        self, opponent: Self, hypothetical_my_action: int
    ) -> int:
        """
        Predicts opponent's next move given their history and what I would play now with a Naive Learner model.
        """
        if not opponent.history:
            return 2

        last_opp = opponent.history[-1]
        payoff_opp = 0
        if hypothetical_my_action + last_opp <= 5:
            payoff_opp = last_opp

        if payoff_opp > 0:
            return min(5, last_opp + 1) if random() < 0.2 else last_opp
        else:
            return max(0, last_opp - 1)

    def strategy(self, opponent: Self) -> int:
        if not opponent.history:
            return 2

        prev_my_act = self.history[-1]
        prev_opp_act = opponent.history[-1]
        _, prev_opp_pay = self.game.evaluate_result(prev_my_act, prev_opp_act)

        predicted_opp_act = prev_opp_act
        if prev_opp_pay == 0:
            predicted_opp_act = max(0, prev_opp_act - 1)
        else:
            predicted_opp_act = prev_opp_act

        best_act = 0
        best_pay = -1

        for act in self.game.actions:
            pay, _ = self.game.evaluate_result(act, predicted_opp_act)
            if pay > best_pay:
                best_pay = pay
                best_act = act
            elif pay == best_pay and act > best_act:
                best_act = act

        return best_act
