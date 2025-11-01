import unittest
from limited_sum.game import Game, ACTIONS, THRESHOLD
from limited_sum.player import *


class DummyGame(Game):
    """Implementación mínima de Game solo para testing de Players."""

    @property
    def payoff_matrix(self):
        import numpy as np

        return np.zeros((6, 6, 2), dtype=int)

    def evaluate_result(self, a1, a2):
        return a1, a2


class DummyOpponent(Player):
    """Oponente ficticio para probar reacciones basadas en el historial."""

    def __init__(self, game):
        super().__init__(game)

    def strategy(self, opponent: Player) -> int:
        return 0


class TestAlways0(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.p = Always0(self.game)
        self.opp = DummyOpponent(self.game)

    def test_strategy_always_returns_0(self):
        for _ in range(10):
            self.assertEqual(self.p.strategy(self.opp), 0)


class TestAlways3(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.p = Always3(self.game)
        self.opp = DummyOpponent(self.game)

    def test_strategy_always_returns_3(self):
        for _ in range(10):
            self.assertEqual(self.p.strategy(self.opp), 3)


class TestUniformRandom(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.p = UniformRandom(self.game)
        self.opp = DummyOpponent(self.game)

    def test_strategy_returns_valid_action(self):
        for _ in range(100):
            action = self.p.strategy(self.opp)
            self.assertIn(action, ACTIONS)

    def test_randomness_distribution(self):
        """Comprueba que las acciones no sean todas iguales (test no determinista)."""
        actions = [self.p.strategy(self.opp) for _ in range(200)]
        unique_actions = set(actions)
        # Debe haber más de una acción distinta si realmente es aleatorio
        self.assertGreater(len(unique_actions), 1)


class TestFocal5(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.p = Focal5(self.game)
        self.opp = DummyOpponent(self.game)

    def test_first_round_returns_coordination_action(self):
        self.assertEqual(self.p.strategy(self.opp), Focal5.COORDINATION_ACTION)

    def test_second_round_coordinates_to_sum_5(self):
        # Simula que el oponente jugó 2 la ronda anterior
        self.opp.history.append(2)
        action = self.p.strategy(self.opp)
        # Debería intentar jugar 5 - 2 = 3
        self.assertEqual(action, 3)

    def test_action_is_clipped_to_valid_range(self):
        # Oponente jugó algo alto → resultado negativo
        self.opp.history.append(6)
        action = self.p.strategy(self.opp)
        self.assertEqual(action, 0)

        # Oponente jugó 0 → intenta jugar 5, que está dentro del rango
        self.opp.history[-1] = 0
        action = self.p.strategy(self.opp)
        self.assertEqual(action, 5)

    def test_multiple_rounds_follow_pattern(self):
        self.opp.history = [3, 2, 4]
        action = self.p.strategy(self.opp)
        # último fue 4 → debería intentar 1
        self.assertEqual(action, 1)


class TestTitForTat(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.player = TitForTat(self.game)
        self.opponent = DummyOpponent(self.game)

    def test_first_round_returns_cooperative_action(self):
        self.assertEqual(
            self.player.strategy(self.opponent), TitForTat.COOPERATIVE_ACTION
        )

    def test_reacts_with_last_opponent_action(self):
        self.opponent.history.append(4)
        self.assertEqual(self.player.strategy(self.opponent), 4)
        self.opponent.history.append(1)
        self.assertEqual(self.player.strategy(self.opponent), 1)


class TestCastigadorInfernal(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.player = CastigadorInfernal(self.game)
        self.opponent = DummyOpponent(self.game)
        self.player.clean_history()
        self.opponent.clean_history()

    def test_first_round_returns_2(self):
        self.assertEqual(self.player.strategy(self.opponent), 2)

    def test_increments_cooperation_score_on_cooperation(self):
        self.player.history.append(2)
        self.opponent.history.append(3)  # <= 3 is cooperation
        self.player.strategy(self.opponent)
        self.assertGreater(self.player.cooperation_score, 0)

    def test_decrements_cooperation_score_on_greedy(self):
        self.player.history.append(2)
        self.opponent.history.append(4)  # > 3 is greedy
        self.player.strategy(self.opponent)
        self.assertLess(self.player.cooperation_score, 0)

    def test_enters_punishment_mode_on_greedy_average(self):
        self.player.history.append(2)
        self.opponent.history.extend([5, 5, 5, 5, 5])
        action = self.player.strategy(self.opponent)
        self.assertTrue(self.player.punishment_mode)
        self.assertEqual(action, self.opponent.history[-1])

    def test_punishment_mode_returns_last_opponent_action_for_two_rounds(self):
        self.player.history.append(2)
        self.player.punishment_mode = True
        self.player.punishment_rounds = 0
        self.opponent.history.append(4)
        # first punishment round
        action1 = self.player.strategy(self.opponent)
        self.assertEqual(action1, 4)
        self.assertTrue(self.player.punishment_mode)
        # second punishment round
        action2 = self.player.strategy(self.opponent)
        self.assertEqual(action2, 4)
        self.assertTrue(self.player.punishment_mode)
        # third round resets punishment mode
        action3 = self.player.strategy(self.opponent)
        self.assertEqual(action3, 2)
        self.assertFalse(self.player.punishment_mode)

    def test_returns_coordination_action_when_not_in_punishment(self):
        self.player.history.append(2)
        self.opponent.history.append(3)
        action = self.player.strategy(self.opponent)
        self.assertEqual(action, 5 - 3)

    def test_default_fallback(self):
        self.player.history.append(2)
        self.opponent.history.extend([2, 3, 4])  # promedio = (2+3+4)/3 = 3.0 <= 3.5
        self.player.cooperation_score = 0
        action = self.player.strategy(self.opponent)
        self.assertEqual(action, 2)


class TestDeterministicSimpletron(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()

    def test_starts_cooperating_when_pessimist_false(self):
        p = Deterministic_simpletron(self.game, pesimist_start=False)
        self.assertEqual(p.strategy(DummyOpponent(self.game)), 2)

    def test_starts_greedy_when_pessimist_true(self):
        p = Deterministic_simpletron(self.game, pesimist_start=True)
        self.assertEqual(p.strategy(DummyOpponent(self.game)), 3)

    def test_switches_punish_mode_on_greedy_opponent(self):
        p = Deterministic_simpletron(self.game)
        p.history.append(2)  # last move
        opponent = DummyOpponent(self.game)
        opponent.history.append(3)  # greedy
        p.strategy(opponent)
        self.assertTrue(p.do_punish)

        # Opponent again greedy toggles back punish off
        opponent.history.append(4)
        p.strategy(opponent)
        self.assertFalse(p.do_punish)

    def test_punish_mode_returns_correct_action_basic(self):
        p = Deterministic_simpletron(self.game)
        p.history.append(2)
        opponent = DummyOpponent(self.game)
        opponent.history.append(3)  # greedy triggers punish
        my_action = p.strategy(opponent)
        self.assertTrue(p.do_punish)
        # With tic_for_tat_punishment=False returns 3 during punish
        self.assertEqual(my_action, 3)

    def test_punish_mode_returns_last_opponent_action_tit_for_tat(self):
        p = Deterministic_simpletron(self.game, tic_for_tat_punishment=True)
        p.history.append(2)
        opponent = DummyOpponent(self.game)
        opponent.history.append(3)
        my_action = p.strategy(opponent)
        self.assertTrue(p.do_punish)
        # Punish returns last opponent action
        self.assertEqual(my_action, 3)

    def test_not_punish_returns_last_own_action(self):
        p = Deterministic_simpletron(self.game)
        p.history.append(2)
        opponent = DummyOpponent(self.game)
        opponent.history.append(1)  # not greedy
        p.do_punish = False
        action = p.strategy(opponent)
        self.assertEqual(action, 2)

    def switches(self):
        p = Deterministic_simpletron(self.game, tic_for_tat_punishment=True)
        p.history.append(2)
        opponent = DummyOpponent(self.game)
        opponent.history.append(3)
        p.strategy(opponent)
        self.assertTrue(p.do_punish)
        # Punish returns last opponent action
        self.assertEqual(p.strategy(opponent), 2)

class TestPermissiveTitForTat(unittest.TestCase):
    
    def setUp(self):
        # Configuración común: inicializa el juego y el valor de paciencia por defecto
        self.game = DummyGame()
        self.DEFAULT_PATIENCE = 3

    # Test 1: Comprueba la inicialización de la paciencia por defecto y personalizada
    def test_initialization_patience(self):
        p_default = PermissiveTitForTat(self.game)
        self.assertEqual(p_default.patience, self.DEFAULT_PATIENCE)
        self.assertEqual(p_default.INITIAL_PATIENCE, self.DEFAULT_PATIENCE)

        p_custom = PermissiveTitForTat(self.game, initial_patience=5)
        self.assertEqual(p_custom.patience, 5)
        self.assertEqual(p_custom.INITIAL_PATIENCE, 5)

    # Test 2: Comprueba la acción inicial cuando no hay historial
    def test_initial_action_no_history(self):
        p = PermissiveTitForTat(self.game)
        opponent = DummyOpponent(self.game)
        # Debe devolver 3 (initial action)
        self.assertEqual(p.strategy(opponent), 3) 
        # La paciencia no debe cambiar en este punto
        self.assertEqual(p.patience, self.DEFAULT_PATIENCE)

    # Test 3: Comprueba el comportamiento Tit-for-Tat (devolver la acción del oponente)
    def test_basic_tit_for_tat_action(self):
        p = PermissiveTitForTat(self.game, initial_patience=2)
        opponent = DummyOpponent(self.game)
        
        # Oponente elige 4 (codicioso). Y se queda sin paciencia.
        opponent.history.append(4)
        self.assertEqual(p.strategy(opponent), p.COOPERATIVE_ACTION)
        # Oponente elige 4 (codicioso). La acción de PFTFT debe ser 4.
        opponent.history.append(4)
        self.assertEqual(p.strategy(opponent), 4)

        # Oponente elige 1 (cooperativo). La acción de PFTFT debe ser Cooperativa de nuevo.
        opponent.history.append(1)
        self.assertEqual(p.strategy(opponent), p.COOPERATIVE_ACTION)

    # Test 4: Comprueba la reducción de paciencia con acciones >= 3
    def test_patience_reduction_on_greedy_opponent(self):
        p = PermissiveTitForTat(self.game) # Paciencia inicial 3
        opponent = DummyOpponent(self.game)
        
        # Turno 1: Oponente elige 3 (>= 3) -> paciencia 3 -> 2
        opponent.history.append(3)
        p.strategy(opponent)
        self.assertEqual(p.patience, 2)
        
        # Turno 2: Oponente elige 5 (>= 3) -> paciencia 2 -> 1
        opponent.history.append(5)
        p.strategy(opponent)
        self.assertEqual(p.patience, 1)

    # Test 5: Comprueba el reset de paciencia con acciones < 3
    def test_patience_reset_on_cooperative_opponent(self):
        # Usar paciencia inicial 5 para distinguirlo del valor de reducción
        initial_patience = 5
        p = PermissiveTitForTat(self.game, initial_patience=initial_patience)
        opponent = DummyOpponent(self.game)

        # 1. Reducir la paciencia primero
        opponent.history.append(4) # Paciencia: 5 -> 4
        p.strategy(opponent)
        opponent.history.append(3) # Paciencia: 4 -> 3
        p.strategy(opponent)
        self.assertEqual(p.patience, 3)
        
        # 2. Oponente elige 2 (< 3) -> paciencia debe resetearse a 5
        opponent.history.append(2)
        p.strategy(opponent)
        self.assertEqual(p.patience, initial_patience)
        
        # 3. Oponente elige 1 (< 3) -> paciencia se mantiene en 5
        opponent.history.append(1)
        p.strategy(opponent)
        self.assertEqual(p.patience, initial_patience)

    # Test 6: Comprueba que la paciencia no baja de 0 (paciencia mínima)
    def test_patience_does_not_go_below_zero(self):
        initial_patience = 1
        p = PermissiveTitForTat(self.game, initial_patience=initial_patience)
        opponent = DummyOpponent(self.game)
        
        # Turno 1: Oponente elige 4 (>= 3) -> paciencia 1 -> 0
        opponent.history.append(4)
        p.strategy(opponent)
        self.assertEqual(p.patience, 0)
        
        # Turno 2: Oponente elige 5 (>= 3) -> paciencia 0. max(0, 0-1) = 0
        opponent.history.append(5)
        p.strategy(opponent)
        self.assertEqual(p.patience, 0)
        
        # La acción devuelta sigue siendo 5 (Tit-for-Tat)
        self.assertEqual(p.strategy(opponent), 5)
# ====================================================================
# TESTS UNITARIOS PARA GRIMTRIGGER
# ====================================================================

class TestGrimTrigger(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.COOP = 2
        self.DEFECT = 3

    # Test 1: Comprueba cooperación inicial y estado
    def test_initial_cooperation(self):
        gt = GrimTrigger(self.game)
        opponent = DummyOpponent(self.game)
        self.assertEqual(gt.strategy(opponent), self.COOP)
        self.assertFalse(gt.triggered)

    # Test 2: Mantiene la cooperación si el oponente coopera
    def test_maintain_cooperation(self):
        gt = GrimTrigger(self.game)
        opponent = DummyOpponent(self.game)
        opponent.history = [self.COOP, 1]
        self.assertEqual(gt.strategy(opponent), self.COOP)
        self.assertFalse(gt.triggered)

    # Test 3: Se activa el castigo al detectar la deserción (acción 3)
    def test_trigger_on_defection_3(self):
        gt = GrimTrigger(self.game)
        opponent = DummyOpponent(self.game) # Defección en la R2
        opponent.history.extend([self.COOP, self.DEFECT])
        gt.history.append(self.COOP) # Simular mi acción previa
        self.assertEqual(gt.strategy(opponent), self.DEFECT)
        self.assertTrue(gt.triggered)

    # Test 4: El castigo es permanente (mantiene 3 incluso si el oponente coopera)
    def test_permanent_punishment(self):
        gt = GrimTrigger(self.game)
        gt.triggered = True # Estado de castigo ya activo
        
        # Oponente coopera (acción 2) en la última ronda, pero el estado es permanente.
        opponent = DummyOpponent(self.game)
        opponent.history.extend([self.DEFECT, self.COOP])
        self.assertEqual(gt.strategy(opponent), self.DEFECT)
        self.assertTrue(gt.triggered)


# ====================================================================
# TESTS UNITARIOS PARA GENEROUSTITFORTAT
# ====================================================================

class TestGenerousTitForTat(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.COOP = 2
        self.DEFECT = 3

    # Test 1: Comprueba cooperación inicial
    def test_initial_cooperation(self):
        gtft = GenerousTitForTat(self.game)
        opponent = DummyOpponent(self.game)
        self.assertEqual(gtft.strategy(opponent), self.COOP)

    # Test 2: Sigue a TFT cuando el oponente coopera
    def test_follows_tft_on_cooperation(self):
        gtft = GenerousTitForTat(self.game)
        opponent = DummyOpponent(self.game)
        opponent.history=[self.COOP]
        self.assertEqual(gtft.strategy(opponent), self.COOP)

    # Test 3: Castiga (comportamiento TFT) si la generosidad es 0.0
    def test_punishes_if_not_generous(self):
        # Generosidad 0.0 -> siempre castiga ante deserción (4 > 2)
        gtft = GenerousTitForTat(self.game, prob_generosidad=0.0)
        opponent = DummyOpponent(self.game)
        opponent.history=[4] 
        self.assertEqual(gtft.strategy(opponent), self.DEFECT)

    # Test 4: Perdona (comportamiento generoso) si la generosidad es 1.0
    def test_always_forgives_if_fully_generous(self):
        # Generosidad 1.0 -> siempre coopera ante deserción (4 > 2)
        gtft = GenerousTitForTat(self.game, prob_generosidad=1.0)
        opponent = DummyOpponent(self.game)
        opponent.history=[4]
        self.assertEqual(gtft.strategy(opponent), self.COOP)

    # Test 5: Comprueba la configuración de acciones personalizadas
    def test_configurable_actions(self):
        # Coop=1, Punish=4. Generosidad=0.0 (para probar castigo)
        gtft = GenerousTitForTat(self.game, accion_cooperativa=1, accion_castigo=4, prob_generosidad=0.0)
        
        # Acción inicial (debe ser 1)
        self.assertEqual(gtft.strategy(DummyOpponent(self.game)), 1) 
        
        # Castigo ante deserción del oponente (3 > 1) (debe ser 4)
        opponent = DummyOpponent(self.game)
        opponent.history=[3] 
        self.assertEqual(gtft.strategy(opponent), 4)


# ====================================================================
# TESTS UNITARIOS PARA CONTRITETITFORTAT
# ====================================================================

class TestContriteTitForTat(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.COOP = 2
        self.DEFECT = 3

    # Test 1: Comprueba cooperación inicial
    def test_initial_cooperation(self):
        ctft = ContriteTitForTat(self.game)
        opponent = DummyOpponent(self.game)
        self.assertEqual(ctft.strategy(opponent), self.COOP)

    # Test 2: Juega TFT después de una ronda exitosa (Pago > 0)
    def test_plays_tft_on_success(self):
        ctft = ContriteTitForTat(self.game)
        ctft.history = [self.COOP]
        ctft.payoff_history = [3] # Éxito
        
        # El oponente deserta (acción 4 > 2). CTFT juega TFT -> castiga (3).
        opponent = DummyOpponent(self.game)
        opponent.history=[4]
        self.assertEqual(ctft.strategy(opponent), self.DEFECT)

    # Test 3: Se arrepiente (Coopera) después de una ronda fallida (Pago = 0)
    def test_repents_on_failure(self):
        ctft = ContriteTitForTat(self.game)
        ctft.history = [self.DEFECT]
        ctft.payoff_history = [0] # Fracaso
        
        # El oponente deserta (acción 4). CTFT se arrepiente -> coopera (2).
        opponent = DummyOpponent(self.game)
        opponent.history=[4]
        self.assertEqual(ctft.strategy(opponent), self.COOP)
        
    # Test 4: Se arrepiente incluso si el oponente cooperó (Pago = 0)
    def test_repents_even_if_opponent_cooperated(self):
        # Pago=0 ocurre en (3,3), (4,1), (5,0). 
        # Simular (3,3) donde yo jugué 3 y el oponente 3, y mi pago fue 0.
        ctft = ContriteTitForTat(self.game)
        ctft.history = [self.DEFECT]
        ctft.payoff_history = [0] # Fracaso
        
        opponent = DummyOpponent(self.game) # Oponente juega 3
        opponent.history=[self.DEFECT]
        self.assertEqual(ctft.strategy(opponent), self.COOP) # Debe arrepentirse (2)


# ====================================================================
# TESTS UNITARIOS PARA ADAPTIVEPAVLOV
# ====================================================================

class TestAdaptivePavlov(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame()
        self.COOP = 2
        self.DEFECT = 3

    # Test 1: Comprueba cooperación inicial
    def test_initial_cooperation(self):
        ap = AdaptivePavlov(self.game)
        opponent = DummyOpponent(self.game)
        self.assertEqual(ap.strategy(opponent), self.COOP)

    # Test 2: Win-Stay (mantiene acción) después de éxito (Pago > 0)
    def test_win_stay(self):
        ap = AdaptivePavlov(self.game)
        ap.history = [self.DEFECT] # Mi última acción
        ap.payoff_history = [3] # Éxito
        
        opponent = DummyOpponent(self.game) 
        self.assertEqual(ap.strategy(opponent), self.DEFECT) # Debe repetir 3

    # Test 3: Lose-Shift ('toggle', COOP -> DEFECT)
    def test_lose_shift_toggle_coop_to_defect(self):
        ap = AdaptivePavlov(self.game, shift_strategy='toggle')
        ap.history = [self.COOP] # Mi última acción fue 2
        ap.payoff_history = [0] # Fracaso
        
        opponent = DummyOpponent(self.game) 
        self.assertEqual(ap.strategy(opponent), self.DEFECT) # Debe cambiar a 3

    # Test 4: Lose-Shift ('toggle', DEFECT -> COOP)
    def test_lose_shift_toggle_defect_to_coop(self):
        ap = AdaptivePavlov(self.game, shift_strategy='toggle')
        ap.history = [self.DEFECT] # Mi última acción fue 3
        ap.payoff_history = [0] # Fracaso
        
        opponent = DummyOpponent(self.game) 
        self.assertEqual(ap.strategy(opponent), self.COOP) # Debe cambiar a 2

    # Test 5: Lose-Shift ('always_coop') - Siempre coopera después de fracaso
    def test_lose_shift_always_coop(self):
        ap = AdaptivePavlov(self.game, shift_strategy='always_coop')
        ap.history = [self.DEFECT] # Mi última acción fue 3
        ap.payoff_history = [0] # Fracaso
        
        opponent = DummyOpponent(self.game) 
        self.assertEqual(ap.strategy(opponent), self.COOP) # Debe cambiar a 2

# ====================================================================
# TESTS UNITARIOS PARA DETECTIVE AVANZADO
# ====================================================================

class TestDetective(unittest.TestCase):
    def setUp(self):
        self.game = DummyGame(threshold=5)
        self.PROBE_SEQ = [2, 3, 0, 5]
        self.PROBE_LEN = 4
        self.COOP = 2
        self.DEFECT = 3

    # Test 1: Juega la secuencia de sondeo
    def test_plays_probe_sequence(self):
        det = Detective(self.game)
        opponent = DummyOpponent(self.game)
        for i in range(self.PROBE_LEN):
            action = det.strategy(opponent)
            self.assertEqual(action, self.PROBE_SEQ[i])
            det.history.append(action)
            opponent.history.append(0) 

    # Test 2: Clasifica Tit For Tat (TFT) y adopta mejor respuesta
    def test_classifies_tft_and_responds(self):
        det = Detective(self.game)
        # Mi probe: [2, 3, 0, 5]. Op TFT: [2 (inicial), 2, 3, 0, 5]
        opponent_history = [self.COOP] + self.PROBE_SEQ[:-1] 
        opponent = DummyOpponent(self.game) # Op juega 2 en R5
        opponent.history = opponent_history + [2]
        
        # Ejecutar fase de sondeo
        for i in range(self.PROBE_LEN + 1):
            det.history.append(det.strategy(opponent))
            
        # R5: Fase post-análisis
        self.assertEqual(det.opponent_type, 'TIT_FOR_TAT')
        # La mejor respuesta es TFT (copia la última acción del oponente: 2)
        self.assertEqual(det.strategy(opponent), 2) 

    # Test 3: Clasifica Focal 5 y adopta mejor respuesta (coordinación)
    def test_classifies_focal_5_and_responds(self):
        det = Detective(self.game)
        # Mi probe: [2, 3, 0, 5]. Op Focal 5: [3, 3, 2, 5]
        opponent_history = [3, 3, 2, 5]
        opponent = DummyOpponent(self.game) # Op juega 1 en R5
        opponent.history=opponent_history + [0]
        
        # Ejecutar fase de sondeo
        for i in range(self.PROBE_LEN+1):
            det.history.append(det.strategy(opponent))
        # R5: Fase post-análisis
        self.assertEqual(det.opponent_type, 'FOCAL_5')
        # La mejor respuesta es 5 - 0 = 5
        self.assertEqual(det.strategy(opponent), 5) 

    # Test 4: Clasifica Always 3 y explota (juega 3)
    def test_classifies_always_3_and_responds(self):
        det = Detective(self.game)
        opponent_history = [3] * self.PROBE_LEN 
        opponent = DummyOpponent(self.game) # Op sigue en 3
        opponent.history=opponent_history + [self.DEFECT]
        
        # Ejecutar fase de sondeo
        for i in range(self.PROBE_LEN + 1):
            det.history.append(det.strategy(opponent))
            
        # R5: Fase post-análisis
        self.assertEqual(det.opponent_type, 'ALWAYS_3')
        # La mejor respuesta es 3 (PUNISH_ACTION) para el caso de suma > 5
        self.assertIn(det.strategy(opponent), [2,3])

# ====================================================================
# TESTS UNITARIOS PARA FOCAL 5
# ====================================================================


class TestFocal5(unittest.TestCase):
    
    def setUp(self):
        """Configura el entorno para cada test."""
        # Es crucial que el DummyGame se inicialice con threshold=5
        self.game = DummyGame(threshold=5)
        self.player = Focal5(self.game)
        self.opponent = DummyOpponent(self.game)

    # Test 1: Comprueba la acción inicial (Ronda 1)
    def test_initial_action(self):
        """
        Prueba que la primera acción (sin historial del oponente) 
        es COORDINATION_ACTION (3).
        """
        # Verificamos que el historial está vacío
        self.assertEqual(self.opponent.history, [])
        # Comprobamos la acción
        self.assertEqual(self.player.strategy(self.opponent), self.player.COORDINATION_ACTION)

    # Test 2: Adaptación estándar (Oponente juega 2)
    def test_adaptation_opponent_plays_2(self):
        """
        Prueba que si el oponente jugó 2, el jugador responde 3.
        (Target: 5 - 2 = 3)
        """
        self.opponent.history = [2] # Última jugada del oponente
        self.assertEqual(self.player.strategy(self.opponent), 3)

    # Test 3: Adaptación al límite superior (Oponente juega 0)
    def test_adaptation_opponent_plays_0(self):
        """
        Prueba que si el oponente jugó 0, el jugador responde 5.
        (Target: 5 - 0 = 5)
        """
        self.opponent.history = [0]
        self.assertEqual(self.player.strategy(self.opponent), 5)

    # Test 4: Adaptación al límite inferior (Oponente juega 5)
    def test_adaptation_opponent_plays_5(self):
        """
        Prueba que si el oponente jugó 5, el jugador responde 0.
        (Target: 5 - 5 = 0)
        """
        self.opponent.history = [5]
        self.assertEqual(self.player.strategy(self.opponent), 0)

    # Test 5: Adaptación (Oponente juega 4)
    def test_adaptation_opponent_plays_4(self):
        """
        Prueba que si el oponente jugó 4, el jugador responde 1.
        (Target: 5 - 4 = 1)
        """
        self.opponent.history = [4]
        self.assertEqual(self.player.strategy(self.opponent), 1)

    # Test 6: Clipping (Recorte a 0 si el oponente juega > 5)
    def test_clipping_low(self):
        """
        Prueba que la acción se recorta a 0 si el oponente juega un número alto.
        (Target: 5 - 10 = -5, Clipped: 0)
        """
        self.opponent.history = [10] # Jugada alta (fuera de rango)
        self.assertEqual(self.player.strategy(self.opponent), 0)

    # Test 7: Clipping (Recorte a 5 si el oponente juega < 0)
    def test_clipping_high(self):
        """
        Prueba que la acción se recorta a 5 si el oponente juega un número negativo.
        (Target: 5 - (-2) = 7, Clipped: 5)
        """
        self.opponent.history = [-2] # Jugada baja (fuera de rango)
        self.assertEqual(self.player.strategy(self.opponent), 5)

if __name__ == "__main__":
    unittest.main()