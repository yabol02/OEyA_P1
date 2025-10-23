import unittest
from limited_sum.game import Game, ACTIONS
from limited_sum.player import *
from limited_sum.match import Match


class SimpleGame(Game):
    """
    Implementación concreta mínima del juego para pruebas.
    La recompensa es simplemente (a1, a2) si la suma <= threshold, si no (0, 0).
    """
    @property
    def payoff_matrix(self):
        import numpy as np
        return np.array(
            [
                [(i, j) if i + j <= self.threshold else (0, 0) for j in self.actions]
                for i in self.actions
            ],
            dtype=object
        )

    def evaluate_result(self, a1, a2):
        if a1 + a2 <= self.threshold:
            return a1, a2
        return 0, 0


class TestMatch(unittest.TestCase):
    def setUp(self):
        self.game = SimpleGame()
        self.p1 = Always0(self.game)
        self.p2 = Always0(self.game)

    def test_initialization(self):
        match = Match(self.p1, self.p2, n_rounds=5)
        self.assertEqual(match.n_rounds, 5)
        self.assertEqual(match.error, 0.0)
        self.assertEqual(match.score, (0.0, 0.0))
        self.assertEqual(self.p1.history, [])
        self.assertEqual(self.p2.history, [])

    def test_play_no_error(self):
        """Ambos jugadores juegan siempre 0, sin error."""
        match = Match(self.p1, self.p2, n_rounds=3, error=0.0)
        match.play(do_print=False)

        # Cada ronda da payoff (0, 0), total = (0, 0)
        self.assertEqual(match.score, (0.0, 0.0))
        self.assertEqual(len(self.p1.history), 3)
        self.assertEqual(len(self.p2.history), 3)

    def test_play_with_threshold(self):
        """Verifica que el resultado sea 0 si excede el threshold."""
        # Redefinimos el juego con threshold muy bajo
        low_game = SimpleGame(threshold=0)
        p1 = Always0(low_game)
        p2 = Always0(low_game)
        match = Match(p1, p2, n_rounds=2)
        match.play()

        # Como 0+0 <= 0, el payoff sigue siendo (0, 0)
        self.assertEqual(match.score, (0.0, 0.0))

    def test_invalid_rounds(self):
        """Verifica que lanzar un match con n_rounds <= 0 falle."""
        with self.assertRaises(AssertionError):
            Match(self.p1, self.p2, n_rounds=0)

    def test_compute_scores_consistency(self):
        """Verifica que los puntajes dentro del match coincidan con compute_scores()."""
        match = Match(self.p1, self.p2, n_rounds=4)
        match.play()
        s1, s2 = self.p1.compute_scores(self.p2)
        self.assertAlmostEqual(match.score[0], s1)
        self.assertAlmostEqual(match.score[1], s2)


if __name__ == "__main__":
    unittest.main()
