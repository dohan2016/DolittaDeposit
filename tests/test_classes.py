import unittest
from modules.GestionnaireAcces import GestionnaireAcces

class TestGestionnaireAcces(unittest.TestCase):
    def test_ajout_utilisateur(self):
        g = GestionnaireAcces()
        g.ajouter_utilisateur("Alice", "alice@example.com")
        self.assertEqual(len(g.utilisateurs), 1)

    def test_suppression_utilisateur(self):
        g = GestionnaireAcces()
        g.ajouter_utilisateur("Bob", "bob@example.com")
        g.supprimer_utilisateur("bob@example.com")
        self.assertEqual(len(g.utilisateurs), 0)

if __name__ == "__main__":
    unittest.main()
