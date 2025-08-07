import unittest
from modules.Utilisateur import Utilisateur
from modules.GestionnaireAcces import GestionnaireAcces

class TestUtilisateur(unittest.TestCase):
    def test_creation_utilisateur(self):
        u = Utilisateur("Alice", "alice@example.com", "12345", actif=True)
        self.assertEqual(u.nom, "Alice")
        self.assertEqual(u.email, "alice@example.com")
        self.assertEqual(u.mot_de_passe, "12345")
        self.assertTrue(u.actif)

    def test_activation_desactivation(self):
        u = Utilisateur("Bob", "bob@example.com", "abcde", actif=False)
        u.activer()
        self.assertTrue(u.actif)
        u.desactiver()
        self.assertFalse(u.actif)

    def test_to_dict(self):
        u = Utilisateur("Claire", "claire@example.com", "xyz", actif=True)
        d = u.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["email"], "claire@example.com")
        self.assertTrue(d["actif"])

class TestGestionnaireAcces(unittest.TestCase):
    def setUp(self):
        self.g = GestionnaireAcces()
        self.u1 = Utilisateur("Dan", "dan@example.com", "motdepasse")
        self.u2 = Utilisateur("Emma", "emma@example.com", "secret")

    def test_ajouter_utilisateur(self):
        self.g.ajouter_utilisateur(self.u1)
        self.assertEqual(len(self.g.utilisateurs), 1)
        self.assertEqual(self.g.utilisateurs[0].email, "dan@example.com")

    def test_supprimer_utilisateur(self):
        self.g.ajouter_utilisateur(self.u1)
        self.g.supprimer_utilisateur("dan@example.com")
        self.assertEqual(len(self.g.utilisateurs), 0)

    def test_get_utilisateur(self):
        self.g.ajouter_utilisateur(self.u2)
        result = self.g.get_utilisateur("emma@example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result.nom, "Emma")

    def test_generer_mot_de_passe(self):
        mdp = self.g.generer_mot_de_passe(10)
        self.assertEqual(len(mdp), 10)
        self.assertIsInstance(mdp, str)

if __name__ == '__main__':
    unittest.main()
