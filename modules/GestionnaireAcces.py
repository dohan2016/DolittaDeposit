from modules.Utilisateur import Utilisateur
import json

class GestionnaireAcces:
    def __init__(self):
        self.utilisateurs = []

    def ajouter_utilisateur(self, utilisateur):
        self.utilisateurs.append(utilisateur)

    def supprimer_utilisateur(self, email):
        self.utilisateurs = [u for u in self.utilisateurs if u.email != email]

    def get_utilisateur(self, email):
        for u in self.utilisateurs:
            if u.email == email:
                return u
        return None

    def generer_mot_de_passe(self, longueur=8):
        import random
        import string
        caracteres = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(random.choice(caracteres) for _ in range(longueur))

    def sauvegarder_json(self, fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in self.utilisateurs], f, indent=4)

    def charger_json(self, fichier):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                self.utilisateurs = [Utilisateur(**d) for d in donnees]
        except FileNotFoundError:
            self.utilisateurs = []
