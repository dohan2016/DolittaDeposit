class Utilisateur:
    def __init__(self, nom, email, mot_de_passe, actif=True):
        self.nom = nom
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.actif = actif

    def activer(self):
        self.actif = True

    def desactiver(self):
        self.actif = False

    def to_dict(self):
        return {
            "nom": self.nom,
            "email": self.email,
            "mot_de_passe": self.mot_de_passe,
            "actif": self.actif
        }
