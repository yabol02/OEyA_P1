from abc import ABC, abstractmethod
from random import choice, random
from typing import Self

from .game import Game


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

        # Main variable of this class that tores the full history of actions performed by the player.
        # Example: [0, 1, 2, 3] → in the first round the player chose 0, in the second round 1, and so on.
        self.history = []

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


# ---------------------------------------------------------------------
# Basic strategies for the limited-sum game
# ---------------------------------------------------------------------


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
    Strategy that chooses an action uniformly at random.
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
        Chooses an action uniformly at random.

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


# ---------------------------------------------------------------------
# Basic strategies for the limited-sum game
# ---------------------------------------------------------------------
class Deterministic_simpletron(Player):
    """Starts cooperating (return 2) if the player cooperates it returns the same value
    If the oponent does not cooperate, it switches the strategy from cooperating to being greedy (return 3) or
    form being greedy to cooperating"""

    def __init__(
        self,
        game: Game,
        name: str = "",
        pesimist_start: bool = False,
        tit_for_tat_punishment: bool = False,
    ):
        """
        Inicializa un agente basado en la estrategia SIMPLETON determinista.

        Parámetros
        ----------
        game : Game
            Objeto del juego al que pertenece el agente.
        name : str, opcional
            Nombre del agente (por defecto una cadena vacía).
        pesimist_start : bool, opcional
            Indica si el agente debe comenzar con una jugada 'greedy' (3) o 'amigable' (2):
            - False → comienza cooperando (valor 2).
            - True  → comienza siendo greedy (valor 3).
        tit_for_tat_punishment : bool, opcional
            Controla el tipo de castigo cuando el oponente es greedy (≥3):
            - False → castigo básico: siempre responde con 3.
            - True  → castigo tipo "tit-for-tat": replica la última acción del oponente.

        Notas
        -----
        El agente sigue la lógica del método SIMPLETON:
        - Si el oponente coopera (<3), repite su último movimiento.
        - Si el oponente no coopera (≥3), cambia al modo opuesto (de cooperar a castigar o viceversa).
        """
        # Inicialización básica del agente
        super(Deterministic_simpletron, self).__init__(game, name)

        # Parámetros de configuración
        self.pesimist_start = pesimist_start
        self.tit_for_tat_punishmnet = tit_for_tat_punishment

        # Bandera interna para saber si el agente está en modo "castigo"
        # (True = aplicar castigo; False = comportamiento normal)
        self.do_punish = False

    def strategy(self, opponent: Player) -> int:
        if len(self.history) == 0:
            # Comienza el juego
            if self.pesimist_start:
                return 3
            else:
                return 2
        # Rondas sucesivas
        # Comprobamos que el contrincante sea greedy
        last_opponent_action = opponent.history[-1]
        if last_opponent_action >= 3:
            # El contrincante es greedy y cambiamos de modo
            self.do_punish = not (self.do_punish)

        if self.do_punish:
            # Vamos punishear
            if self.tit_for_tat_punishmnet:
                return last_opponent_action
            else:
                return 3  # Basico
        else:
            # Comportamiento basico: devolver nuestra ultima opcion opcion sea cual sea
            return self.history[-1]


class PermissiveTitForTat(Player):
    """
    Estrategia Tit-for-Tat permisiva con un atributo de 'paciencia'.
    La paciencia se reduce si el oponente elige una acción >= 3 y se resetea
    si elige una acción < 3.
    """

    INITIAL_ACTION = 3  # JEJE somos malos
    COOPERATIVE_ACTION = 2

    # Define la paciencia inicial o máxima
    INITIAL_PATIENCE = 3

    def __init__(
        self,
        game: Game,
        name: str = "Permissive Tit for Tat",
        initial_patience: int = 3,
    ):
        """
        Inicializa el jugador PermissiveTitForTat.

        :param game: El juego que se está jugando.
        :type game: Game
        :param name: Nombre opcional de la estrategia.
        :type name: str
        :param initial_patience: El valor inicial del atributo de paciencia.
        :type initial_patience: int
        """
        super(PermissiveTitForTat, self).__init__(game, name)
        # Atributo para controlar la paciencia.
        self.patience = initial_patience
        self.INITIAL_PATIENCE = initial_patience

    def strategy(self, opponent: Player) -> int:
        """
        Implementa la lógica de la estrategia:
        1. Responde a la última acción del oponente (como Tit for Tat).
        2. Ajusta la paciencia según la última acción del oponente.

        :param opponent: El jugador oponente.
        :type opponent: Player
        :return: La acción elegida (0 a 5).
        :rtype: int
        """
        if not opponent.history:
            # Si no hay historia, comienza con la acción cooperativa
            return self.INITIAL_ACTION

        last_opponent_action = opponent.history[-1]

        # --- Lógica de ajuste de la paciencia ---

        if last_opponent_action >= 3:
            # Si el oponente es 'codicioso' (elige 3 o más), reduce la paciencia
            self.patience = max(0, self.patience - 1)
        elif last_opponent_action < 3:
            # Si el oponente elige algo menor a 3, resetea la paciencia
            self.patience = self.INITIAL_PATIENCE

        # --- Lógica de la acción ---

        # Elige la acción en función de la última acción del oponente si la paciencia es 0
        # (comportamiento base de Tit-for-Tat)
        if self.patience == 0:
            return last_opponent_action
        else:
            return self.COOPERATIVE_ACTION


class GrimTrigger(Player):
    COOPERATIVE_ACTION = 2
    PUNISHMENT_ACTION = 3  # La deserción más leve

    def __init__(self, game: Game, name: str = "Grim Trigger"):
        super(GrimTrigger, self).__init__(game, name)
        self.triggered = False  # Estado de castigo

    def strategy(self, opponent: Player) -> int:
        # Si ya estamos en modo castigo, castigar para siempre.
        if self.triggered:
            return self.PUNISHMENT_ACTION

        # Revisar el historial del oponente por cualquier deserción pasada
        if not opponent.history:
            return self.COOPERATIVE_ACTION  # Cooperar en la primera ronda

        # Si el oponente desertó en la última ronda (o cualquier ronda anterior)
        # Nota: una versión más estricta revisaría todo el 'opponent.history'
        if opponent.history[-1] > self.COOPERATIVE_ACTION:
            self.triggered = True
            return self.PUNISHMENT_ACTION

        # Si no hay traición, seguir cooperando
        return self.COOPERATIVE_ACTION


class GenerousTitForTat(Player):
    """
    Estrategia Tit-for-Tat Generoso (GTFT).

    Sigue la lógica de TFT (cooperar si el oponente cooperó, castigar si desertó),
    pero con una probabilidad 'prob_generosidad', perdona una deserción
    del oponente y coopera de todos modos.

    Esto es crucial para romper ciclos de castigo mutuo iniciados por un error (ruido).
    """

    def __init__(
        self,
        game: "Game",
        name: str = "Generous TFT",
        accion_cooperativa: int = 2,
        accion_castigo: int = 3,
        prob_generosidad: float = 0.1,
    ):
        """
        Constructor configurable.

        :param accion_cooperativa: La acción a tomar para cooperar (default: 2).
        :param accion_castigo: La acción a tomar para castigar (default: 3).
        :param prob_generosidad: Probabilidad (0.0 a 1.0) de perdonar una deserción.
                                 Un valor común en estudios es 1/3 o 0.1.
        """
        super(GenerousTitForTat, self).__init__(game, name)
        self.COOPERATIVE_ACTION = accion_cooperativa
        self.PUNISHMENT_ACTION = accion_castigo
        self.GENEROSITY_PROB = prob_generosidad

    def strategy(self, opponent: Player) -> int:
        # Cooperar en la primera ronda
        if not opponent.history:
            return self.COOPERATIVE_ACTION

        last_opponent_action = opponent.history[-1]

        # 1. Si el oponente cooperó, nosotros cooperamos
        if last_opponent_action <= self.COOPERATIVE_ACTION:
            return self.COOPERATIVE_ACTION

        # 2. Si el oponente desertó...
        else:
            # 3. Decidir si ser generoso (perdonar)
            if random() < self.GENEROSITY_PROB:
                # Perdón: Romper el ciclo cooperando
                return self.COOPERATIVE_ACTION
            else:
                # Castigo: Seguir la regla de TFT
                return self.PUNISHMENT_ACTION


# --- Otros Modelos Robustos Configurables ---


class ContriteTitForTat(Player):
    """
    Tit-for-Tat Arrepentido (o "Estratega Arrepentido").

    Esta estrategia se enfoca en el *otro* lado del ruido: ¿Qué pasa si *yo*
    causé el problema?

    Su lógica es:
    1. Si la última ronda fue un éxito (Pago > 0), jugar como TFT.
    2. Si la última ronda fue un fracaso (Pago = 0), asumir la culpa (arrepentirse)
       y cooperar, esperando que esto rompa el ciclo de castigo.
    """

    def __init__(
        self,
        game: "Game",
        name: str = "Contrite TFT",
        accion_cooperativa: int = 2,
        accion_castigo: int = 3,
    ):

        super(ContriteTitForTat, self).__init__(game, name)
        self.COOPERATIVE_ACTION = accion_cooperativa
        self.PUNISHMENT_ACTION = accion_castigo

    def strategy(self, opponent: Player) -> int:
        # Cooperar en la primera ronda
        if not self.history:
            return self.COOPERATIVE_ACTION

        my_last_payoff = self._get_last_payoff(opponent)

        # 1. Arrepentimiento: Si el resultado fue 0, cooperar para arreglarlo.
        if my_last_payoff == 0:
            return self.COOPERATIVE_ACTION

        # 2. Éxito: Si el pago fue > 0, jugar como TFT estándar.
        else:
            last_opponent_action = opponent.history[-1]
            if last_opponent_action > self.COOPERATIVE_ACTION:
                return self.PUNISHMENT_ACTION
            else:
                return self.COOPERATIVE_ACTION


class AdaptivePavlov(Player):
    """
    Estrategia Pavlov (Win-Stay, Lose-Shift) Adaptativa.

    La estrategia "Pavlov" simple (vista en la respuesta anterior) alterna
    entre dos acciones. Esta versión permite más flexibilidad en la
    lógica "Lose-Shift" (Perder-Cambiar).
    """

    def __init__(
        self,
        game: "Game",
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
        game: "Game",
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


class HatTricker(Player):
    """
    Player that tries to impose always making 3. It takes the last 3 rounds for insight.
    """

    def __init__(self, game: Game, name: str = "Hat Tricker"):
        super(HatTricker, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        # First three rounds always 3
        play = 3
        if len(opponent.history) >= 3:
            # Detect always 3
            if sum(opponent.history[-3:]) == 9:
                play = 2
            # If opponent is open to cooperate, impose 3
            elif opponent.history[-1] == 2 or opponent.history[-2] == 2:
                play = 3
            else:
                play = choice([2, 3])
        return play


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

    def strategy(self, opponent: Player) -> int:
        return choice([2, 3], weights=self.w)


class AgenteAstuto(Player):
    """
    Una estrategia inteligente y adaptativa que busca el equilibrio entre
    cooperación, explotación y castigo, siguiendo las reglas especificadas.

    Lógica de la estrategia:
    1.  **Prioridad 1 (Defensa):** Si el oponente es codicioso (juega >= 3),
        castigarlo jugando 3 para asegurar un resultado de (0, 0).
    2.  **Prioridad 2 (Seguridad):** Si acabamos de explotar (jugamos 3 o 4
        en la ronda anterior) y el oponente *no* es codicioso,
        debemos cooperar (jugar 2) para evitar patrones y "resetear"
        la paciencia de los oponentes tipo "Permissive Tit-for-Tat".
    3.  **Prioridad 3 (Explotación):** Si el oponente coopera (< 3) y
        nosotros no acabamos de explotar:
        -   Si juega 1: Jugamos 4 (máxima explotación).
        -   Si juega 0 o 2: Con una probabilidad (exploitation_prob),
            jugamos 3 para ganar puntos extra.
    4.  **Prioridad 4 (Cooperación):** Si no se cumple ninguna de las
        condiciones de explotación, cooperamos jugando 2.

    Nunca juega 5.
    """

    # Acción cooperativa estándar
    COOP_ACTION = 2
    # Acción de explotación principal (para oponentes 0 o 2)
    EXPLOIT_ACTION = 3
    # Acción de castigo (para oponentes >= 3)
    PUNISH_ACTION = 3
    # Acción de explotación máxima (para oponentes 1)
    MAX_EXPLOIT_ACTION = 4

    def __init__(
        self, game: Game, name: str = "Agente Astuto", exploitation_prob: float = 0.20
    ):
        """
        Inicializa el Agente Astuto.

        :param game: El juego que se está jugando.
        :param name: Nombre de la estrategia.
        :param exploitation_prob: Probabilidad (0.0 a 1.0) de intentar
                                 explotar a un oponente cooperativo
                                 (que jugó 0 o 2) en un turno dado.
        """
        super(AgenteAstuto, self).__init__(game, name)

        # Estado interno: ¿Acabamos de explotar/castigar (jugar >= 3) en la ronda anterior?
        self.just_exploited = False

        # Probabilidad de ser "listillo"
        self.EXPLOITATION_PROB = exploitation_prob

    def strategy(self, opponent: Player) -> int:

        # Empezamos cooperando para tantear.
        if not self.history:
            self.just_exploited = False
            return self.COOP_ACTION

        last_opponent_action = opponent.history[-1]
        my_action = 0

        # --- PRIORIDAD 1: DEFENSA (Regla Anti-Codicia) ---
        # Frente a agentes que no colaboren (elecciones >=3), vamos a hacer que no puntúen.
        # Frente a alguien que pone siempre 3 vamos a reventarle: si juegan 3, 4 o 5, jugamos 3. (3+3=6, 3+4=7, 3+5=8)
        if last_opponent_action >= 3:
            my_action = self.PUNISH_ACTION
            self.just_exploited = True
            return my_action

        # --- PRIORIDAD 2: SEGURIDAD (Regla "Nunca dos veces") ---
        # Si el oponente está cooperando (< 3), PERO nosotros acabamos de explotar, estamos forzados a cooperar.
        if self.just_exploited:
            # Forzamos la cooperación (jugamos 2) para resetear la paciencia del oponente (PermissiveTFT) y evitar patrones.
            my_action = self.COOP_ACTION
            self.just_exploited = False  # Reseteamos nuestro estado
            return my_action

        # --- PRIORIDAD 3: EXPLOTACIÓN (Oportunismo) ---
        # Si llegamos aquí, significa que:
        # 1. El oponente está cooperando (jugó < 3).
        # 2. Nosotros NO acabamos de explotar (somos "libres" de actuar).

        # Regla: "Si por lo que sea vemos que pone 1s, vamos a poner 4"
        if last_opponent_action == 1:
            my_action = self.MAX_EXPLOIT_ACTION
            self.just_exploited = True
            return my_action

        if last_opponent_action in [0, 2]:
            if random() < self.EXPLOITATION_PROB:
                # ¡Explotar!
                my_action = self.EXPLOIT_ACTION
                self.just_exploited = True  # Marcamos que hemos explotado
                return my_action
            else:
                # No explotamos esta vez, seguimos cooperando.
                my_action = self.COOP_ACTION
                self.just_exploited = False
                return my_action

        # --- PRIORIDAD 4: COOPERACIÓN (Fallback) ---
        # Esta lógica cubre todos los casos (0, 1, 2).
        # Si no se activó la explotación (por probabilidad o regla), la acción por defecto es cooperar.
        my_action = self.COOP_ACTION
        self.just_exploited = False
        return my_action


class WSLS_Adapted(Player):
    "Win-Stay Lose-Shift adaptado a 0..5 con aspiración"

    def __init__(self, game, aspiration=2.5, name="WSLS"):
        super().__init__(game, name)
        self.aspiration = aspiration

    def strategy(self, opponent):
        if not self.history:
            return 2
        last_payoff = self._get_last_payoff(opponent)
        last_action = self.history[-1]
        if last_payoff >= self.aspiration:
            return last_action  # stay
        else:
            # shift: intentar ajustar para evitar colapso. Si el fallo fue por suma>max -> se reduce
            if last_action + opponent.history[-1] > self.game.max_sum:
                return max(0, last_action - 1)
            else:
                return min(5, last_action + 1)


class AWSLS(Player):
    def __init__(
        self, game, A=2.5, delta=1, forgive_prob=0.1, punish_len=2, a0=2, name="AWSLS"
    ):
        super().__init__(game, name)
        self.A = A
        self.delta = delta
        self.f = forgive_prob
        self.k = punish_len
        self.a0 = a0
        self._punish_timer = 0  # contador interno de castigo

    def strategy(self, opponent):
        # primer movimiento
        if not self.history:
            return self.a0
        # si estamos en periodo de castigo: bajar a 0 durante k rondas
        if self._punish_timer > 0:
            return 0
        # calcular último payoff
        last_payoff = self._get_last_payoff(opponent)
        my_last = self.history[-1]
        opp_last = opponent.history[-1]
        # si fue satisfactorio, stay (con posibilidad de explorar/perdonar)
        if last_payoff >= self.A:
            # small forgiveness: con prob f podemos try subir (aprovechar cooperadores)
            if random.random() < self.f:
                return min(5, my_last + self.delta)
            return my_last
        # Si no fue satisfactorio: diagnóstico
        # Caso colapso (sum>max): disminuir
        if my_last + opp_last > self.game.max_sum:
            # si el oponente lo provoca consistentemente, iniciamos castigo temporal
            # detectamos patrón de explotación (si en las últimas 3 rondas_opponente consistentemente > threshold)
            recent = (
                opponent.history[-3:]
                if len(opponent.history) >= 3
                else opponent.history
            )
            if (
                all(o > (self.game.max_sum - my_last) for o in recent)
                and len(recent) >= 2
            ):
                self._punish_timer = self.k  # activar castigo
                return 0
            return max(0, my_last - self.delta)
        # Si el oponente contribuyó poco -> intentar subir para captar más
        if opp_last <= 2:
            return min(5, my_last + self.delta)
        # en otros casos, bajar para evitar colapsos
        return max(0, my_last - self.delta)


class BinarySunset(Player):
    """
    A player that only plays binary numbers (2, 4) and that stars more agressive (4) until the sunset where ir colaborates (2).
    
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


class CopyCat(Player):
    """
    Childish player that copies the opponent's last move.
    """

    def __init__(self, game: Game, name: str = "CopyCat"):
        super(CopyCat, self).__init__(game, name)

    def strategy(self, opponent: Player) -> int:
        """
        Implements the CopyCat strategy:
        1. In the first round, it plays 2 (cooperative move).
        2. In subsequent rounds, it copies the opponent's last move.
        """
        if not opponent.history:
            return 2
        return opponent.history[-1]
