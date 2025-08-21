from dataclasses import dataclass, asdict

@dataclass
class Utilisateur:
    """
    Représente un utilisateur du système.

    Attributs
    ---------
    nom : str
        Nom complet (ou identifiant lisible).
    email : str
        Adresse e-mail unique (sert de clé logique).
    mot_de_passe : str
        Mot de passe en clair ou déjà dérivé/hasher (selon la couche métier).
    actif : bool
        Statut d'activation du compte (True par défaut).
    """
    nom: str
    email: str
    mot_de_passe: str
    actif: bool = True  # actif par défaut à la création

    def activer(self) -> None:
        """Active le compte utilisateur (actif = True)."""
        self.actif = True

    def desactiver(self) -> None:
        """Désactive le compte utilisateur (actif = False)."""
        self.actif = False

    def to_dict(self) -> dict:
        """
        Convertit l'utilisateur en dict natif (utile pour l’export JSON).
        Équivalent à dataclasses.asdict(self).
        """
        return asdict(self)
