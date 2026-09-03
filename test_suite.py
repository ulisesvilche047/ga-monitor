"""
Suite de pruebas unitarias para el monitor de Gameplay Alliance.
"""
import unittest
import json
from ga_monitor import matches_category_filter, format_notification

class TestGAMonitor(unittest.TestCase):
    def setUp(self):
        self.mock_call = {
            "call_id": "GA-2026-017",
            "titulo": "Mundo abierto y RPG",
            "descripcion": "Buscamos datasets de mundo abierto y rol...",
            "tipo": "Marketplace",
            "categorias": ["Action Adventure", "Action RPG", "Souls-like"],
            "horas_totales": 1500.0,
            "horas_subidas": 116.8,
            "sin_limite": False,
            "completo": False,
            "precio_hora_usd": 3.25
        }

    def test_filter_empty_matches_all(self):
        self.assertTrue(matches_category_filter(self.mock_call, []))

    def test_filter_matches_rpg(self):
        self.assertTrue(matches_category_filter(self.mock_call, ["rpg"]))
        self.assertTrue(matches_category_filter(self.mock_call, ["Mundo abierto"]))

    def test_filter_not_matches_racing(self):
        self.assertFalse(matches_category_filter(self.mock_call, ["racing", "simulación"]))

    def test_format_notification(self):
        title, msg = format_notification(self.mock_call, is_reopen=False, dashboard_url="https://gameplayalliance.gg/dashboard/")
        self.assertIn("Nueva Orden Abierta", title)
        self.assertIn("Mundo abierto y RPG", title)
        self.assertIn("GA-2026-017", msg)
        self.assertIn("US$ 3.25 / hora", msg)
        self.assertIn("1500", msg)
        self.assertIn("https://gameplayalliance.gg/dashboard/", msg)

    def test_format_reopen_notification(self):
        title, msg = format_notification(self.mock_call, is_reopen=True)
        self.assertIn("Orden Reabierta", title)

if __name__ == "__main__":
    unittest.main()
