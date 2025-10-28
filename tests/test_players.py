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

if __name__ == "__main__":
    unittest.main()
