"""
Tests unitaires pour modules.gestionnaire_acces.GestionnaireAcces

Ce fichier couvre :
- Ajout et unicité par email (insensibilité à la casse)
- (Dé)activation d'utilisateurs existants et erreur si inconnu
- Suppression avec vérification
- Filtres d'affichage (Tous / Actifs / Inactifs)
- Sauvegarde/Chargement JSON (cas normal, base vide, JSON invalide)
- Validation des entrées (nom/email vides)
- Accès direct par email (get_utilisateur)
"""

import unittest, os, tempfile, json
from modules.gestionnaire_acces import GestionnaireAcces


class TestsGestionnaire(unittest.TestCase):
    def setUp(self):
        # Un gestionnaire neuf à chaque test
        self.g = GestionnaireAcces()

    # ----------------- Tests fournis (avec commentaires) -----------------

    def test_ajout_unicite(self):
        """Deux utilisateurs ne peuvent pas partager le même email."""
        self.g.ajouter_utilisateur('Alice', 'alice@example.com')
        with self.assertRaises(ValueError):
            # même email → doit lever une erreur
            self.g.ajouter_utilisateur('Alice2', 'alice@example.com')

    def test_activer_desactiver(self):
        """Un utilisateur peut être désactivé puis réactivé."""
        self.g.ajouter_utilisateur('Bob', 'bob@example.com')
        self.g.desactiver('bob@example.com')
        self.assertFalse(self.g.get_utilisateur('bob@example.com').actif)
        self.g.activer('bob@example.com')
        self.assertTrue(self.g.get_utilisateur('bob@example.com').actif)

    def test_save_load(self):
        """Sauvegarde dans un JSON puis rechargement dans un nouveau gestionnaire."""
        self.g.ajouter_utilisateur('Cara', 'cara@example.com')
        fd, path = tempfile.mkstemp(suffix='.json'); os.close(fd)
        try:
            self.g.sauvegarder(path)
            g2 = GestionnaireAcces()
            g2.charger(path)
            self.assertEqual(len(g2.utilisateurs), 1)
            self.assertEqual(g2.utilisateurs[0].email, 'cara@example.com')
        finally:
            os.remove(path)

    # ----------------- Nouveaux tests utiles -----------------

    def test_ajout_email_insensible_a_la_casse(self):
        """
        L'unicité d'email doit être vérifiée en ignorant la casse (ex: 'ALICE@...' == 'alice@...').
        """
        self.g.ajouter_utilisateur('Alice', 'ALICE@Example.com')
        with self.assertRaises(ValueError):
            self.g.ajouter_utilisateur('Alice Clone', 'alice@example.com')

        # get_utilisateur devrait accepter l'email en minuscule
        u = self.g.get_utilisateur('alice@example.com')
        self.assertIsNotNone(u)
        self.assertEqual(u.email.lower(), 'alice@example.com')

    def test_validation_entrees_vides(self):
        """
        L'ajout avec nom ou email vides doit échouer.
        (Selon implémentation : ValueError ; on garde ce type pour cohérence)
        """
        with self.assertRaises(ValueError):
            self.g.ajouter_utilisateur('', 'vide@example.com')
        with self.assertRaises(ValueError):
            self.g.ajouter_utilisateur('SansEmail', '')
        with self.assertRaises(ValueError):
            self.g.ajouter_utilisateur('EspacesSeulement', '   ')

    def test_supprimer_utilisateur(self):
        """Suppression d'un utilisateur par email puis vérification d'absence."""
        self.g.ajouter_utilisateur('Del', 'del@example.com')
        self.assertIsNotNone(self.g.get_utilisateur('del@example.com'))
        self.g.supprimer_utilisateur('del@example.com')
        # Après suppression, get_utilisateur devrait échouer (ValueError/KeyError)
        with self.assertRaises((ValueError, KeyError)):
            self.g.get_utilisateur('del@example.com')

    def test_activer_desactiver_inconnu(self):
        """
        (Dé)activer un email inconnu doit lever une erreur.
        On accepte ValueError ou KeyError selon implémentation.
        """
        with self.assertRaises((ValueError, KeyError)):
            self.g.activer('ghost@example.com')
        with self.assertRaises((ValueError, KeyError)):
            self.g.desactiver('ghost@example.com')

    def test_filtres_tous_actifs_inactifs(self):
        """Vérifie la cohérence du filtre de lister_utilisateurs()."""
        self.g.ajouter_utilisateur('A', 'a@example.com')          # actif par défaut ?
        self.g.ajouter_utilisateur('B', 'b@example.com')
        self.g.ajouter_utilisateur('C', 'c@example.com')
        # Désactiver B
        self.g.desactiver('b@example.com')

        # 'Tous' doit renvoyer 3 entrées
        tous = self.g.lister_utilisateurs('Tous')
        self.assertEqual(len(tous), 3)

        # 'Actifs' doit exclure B
        actifs = self.g.lister_utilisateurs('Actifs')
        self.assertTrue(all(u['actif'] for u in actifs))
        self.assertEqual(len(actifs), 2)

        # 'Inactifs' doit contenir uniquement B
        inactifs = self.g.lister_utilisateurs('Inactifs')
        self.assertTrue(all(not u['actif'] for u in inactifs))
        self.assertEqual(len(inactifs), 1)
        self.assertEqual(inactifs[0]['email'].lower(), 'b@example.com')

    def test_sauvegarder_base_vide(self):
        """
        Sauvegarder une base vide doit créer un JSON cohérent (liste vide le plus souvent).
        (L'UI empêche peut-être l'export vide, mais la couche métier peut l'autoriser.)
        """
        fd, path = tempfile.mkstemp(suffix='.json'); os.close(fd)
        try:
            self.g.sauvegarder(path)
            # Le fichier doit exister et contenir au moins une structure JSON valide
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Selon ton implémentation : souvent une liste []
            self.assertTrue(isinstance(data, (list, dict)))
        finally:
            os.remove(path)

    def test_charger_json_invalide(self):
        """
        Charger un fichier JSON invalide doit lever une exception claire.
        """
        fd, path = tempfile.mkstemp(suffix='.json'); os.close(fd)
        try:
            # Écrire du contenu non-JSON
            with open(path, 'w', encoding='utf-8') as f:
                f.write("{invalide: ,,,}")  # pas du JSON valide
            with self.assertRaises(Exception):
                self.g.charger(path)
        finally:
            os.remove(path)

    def test_chargement_remplace_contenu(self):
        """
        Vérifie que charger() remplace/actualise bien la base.
        (On crée un fichier avec 2 utilisateurs et on charge par-dessus un gestionnaire non vide.)
        """
        # Préparer un fichier avec 2 entrées
        fd, path = tempfile.mkstemp(suffix='.json'); os.close(fd)
        try:
            data = [
                {"nom": "U1", "email": "u1@example.com", "mot_de_passe": "x", "actif": True},
                {"nom": "U2", "email": "u2@example.com", "mot_de_passe": "y", "actif": False},
            ]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Mettre un élément initial pour voir s'il est remplacé
            self.g.ajouter_utilisateur('Ancien', 'old@example.com')
            self.g.charger(path)

            # On attend 2 utilisateurs (ceux du fichier) ; 'old@example.com' doit disparaître
            self.assertEqual(len(self.g.utilisateurs), 2)
            emails = {u.email.lower() for u in self.g.utilisateurs}
            self.assertEqual(emails, {"u1@example.com", "u2@example.com"})
        finally:
            os.remove(path)

    def test_get_utilisateur_retourne_objet(self):
        """
        get_utilisateur() doit renvoyer un objet (ex: dataclass Utilisateur),
        pas un dict. On vérifie juste la présence d'attributs.
        """
        self.g.ajouter_utilisateur('Dana', 'dana@example.com')
        u = self.g.get_utilisateur('dana@example.com')
        # Présence d'attributs attendus
        self.assertTrue(hasattr(u, 'nom'))
        self.assertTrue(hasattr(u, 'email'))
        self.assertTrue(hasattr(u, 'actif'))
        self.assertTrue(hasattr(u, 'mot_de_passe'))
        # mot_de_passe doit exister (non vide)
        self.assertTrue(isinstance(u.mot_de_passe, str) and len(u.mot_de_passe) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

