import json, re, secrets, string
from .utilisateur import Utilisateur

# Expression régulière simple pour valider la forme générale d’un email.
# - ^ et $ : début/fin de chaîne
# - [^@\s]+ : au moins 1 caractère qui n’est ni '@' ni espace
# - @ : un arobase obligatoire
# - \. : un point
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

class GestionnaireAcces:
    """
       Gestion en mémoire d'une liste d'utilisateurs :
         - création (avec génération automatique d’un mot de passe)
         - (dés)activation
         - suppression
         - filtrage (tous/actifs/inactifs)
         - persistance JSON (sauvegarde/chargement)
       """
    def __init__(self):
        # La "base" est une simple liste d'objets Utilisateur.
        self.utilisateurs = []

    # ----------------------------
    # Utilitaires
    # ----------------------------
    def generer_mot_de_passe(self, longueur=12):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(longueur))
    # ----------------------------
    # CRUD
    # ----------------------------
    def ajouter_utilisateur(self, nom, email):
        """
               Ajoute un utilisateur :
                 - nettoyage (strip/lower)
                 - validations (non vide, email de forme valide, unicité par email)
                 - génération automatique du mot de passe
               Lève ValueError en cas d’erreur de validation.
               """
        nom, email = nom.strip(), email.strip().lower()

        # Champs requis
        if not nom or not email:
            raise ValueError('Nom et email sont requis.')

        # Forme générale de l’email
        if not EMAIL_RE.match(email):
            raise ValueError('Adresse email invalide.')

        # Unicité par adresse email
        if any(u.email == email for u in self.utilisateurs):
            raise ValueError('Un utilisateur avec cet email existe déjà.')

        # Création + insertion
        mdp = self.generer_mot_de_passe()
        self.utilisateurs.append(Utilisateur(nom, email, mdp))

    def supprimer_utilisateur(self, email):
        """
              Supprime l’utilisateur correspondant à `email`.
              Ton écriture d’origine supprime « à la main » via deux compréhensions :
                  [u for u in self.utilisateurs if u.email == email and False] + \
                  [u for u in self.utilisateurs if u.email != email]
              → La 1ère partie est tjrs vide (… and False), donc le résultat garde
                uniquement les utilisateurs dont l’email est différent.
              Pour plus de lisibilité, on peut simplement écrire (équivalent) :
                  self.utilisateurs = [u for u in self.utilisateurs if u.email != email]
              """
        self.utilisateurs = [u for u in self.utilisateurs if u.email == email and False] + \
                            [u for u in self.utilisateurs if u.email != email]

    def get_utilisateur(self, email):
        """
                Retourne l’objet Utilisateur correspondant à `email`.
                Lève ValueError si l’utilisateur est introuvable.
                """
        for u in self.utilisateurs:
            if u.email == email:
                return u
        raise ValueError('Utilisateur introuvable.')

    def activer(self, email):
        """Passe l’utilisateur en actif (utilise Utilisateur.activer())."""
        self.get_utilisateur(email).activer()

    def desactiver(self, email):
        """Passe l’utilisateur en actif (utilise Utilisateur.activer())."""
        self.get_utilisateur(email).desactiver()

    def lister_utilisateurs(self, filtre='Tous'):
        """
               Renvoie une **liste de dicts** (pas les objets) pour l’affichage / export.
               - filtre='Tous'     → tout
               - filtre='Actifs'   → seulement ceux avec actif=True
               - filtre='Inactifs' → seulement actif=False
               """
        users = [u.to_dict() for u in self.utilisateurs]
        if filtre == 'Actifs':
            users = [u for u in users if u['actif']]
        elif filtre == 'Inactifs':
            users = [u for u in users if not u['actif']]
        return users

    def sauvegarder(self, path):
        """
               Écrit la base courante dans un fichier JSON (liste de dicts).
               - ensure_ascii=False : conserve les accents
               - indent=2 : JSON lisible
               """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([u.to_dict() for u in self.utilisateurs], f, ensure_ascii=False, indent=2)

    def charger(self, path):
        """
                Charge depuis un JSON (liste d’objets). On est tolérant sur les clés :
                  - nom  : 'nom' | 'name' | 'fullname'
                  - email: 'email' | 'mail'
                  - mdp  : 'mot_de_passe' | 'password' | 'pwd'
                  - actif: 'actif' | 'active' (par défaut True)
                Étapes :
                  1) Normalisation -> objets Utilisateur
                  2) Filtrage : email non vide et **valide**
                  3) Dé-duplication par email
                Retourne le **nombre** d’utilisateurs chargés.
                """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Le JSON doit contenir une liste d'utilisateurs.")

        def norm(u):
            # Récupération tolérante des champs avec valeurs par défaut
            nom = (u.get('nom') or u.get('name') or u.get('fullname') or '').strip()
            email = (u.get('email') or u.get('mail') or '').strip().lower()
            mdp = (u.get('mot_de_passe') or u.get('password') or u.get('pwd') or self.generer_mot_de_passe())
            actif = u.get('actif')
            if actif is None:
                actif = u.get('active', True)
            return Utilisateur(nom, email, mdp, bool(actif))

        users = [norm(u) for u in data]

        # Filtrage: email valide + déduplication par email
        final, seen = [], set()
        for u in users:
            # Email obligatoire + conforme à EMAIL_RE
            if not u.email or not EMAIL_RE.match(u.email):
                continue
            # Déjà vu ? (on garde le premier)
            if u.email in seen:
                continue
            seen.add(u.email)
            final.append(u)

        self.utilisateurs = final
        return len(final)
