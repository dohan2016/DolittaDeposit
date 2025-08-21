"""
main.py — Point d'entrée de l'application SDH Security
- Charge l'interface principale .ui
- Applique le thème et l'image de fond
- Connecte le menu aux différentes fenêtres (Gestion, Outils, etc.)
- Gère l'aide contextuelle (F1 / Shift+F1 / What's This)
"""

import os, sys
# Import PyQt5 (widgets, chargement .ui, types de base Qt)
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QShortcut, QLabel, QApplication, QWhatsThis
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt

# Thème visuel (stylesheet + fond d’écran) défini dans theme.py
from theme import apply_theme

# Fonctions qui ouvrent les différentes boîtes de dialogue
from dialogs_logic import (
    ouvrir_dialogue_gestion,
    ouvrir_dialogue_hash,
    ouvrir_dialogue_mdp,
    ouvrir_dialogue_chiffrement,
    ouvrir_dialogue_affichage,
)

# Logique métier de gestion des utilisateurs (CRUD, import/export, filtrage)
from modules.gestionnaire_acces import GestionnaireAcces

# Dossier racine du projet (sert à retrouver les images et .ui)
BASE_DIR = os.path.dirname(__file__)


def _show_help(window, html):
    """
    Affiche une boîte d'aide simple en HTML (titre + contenu).
    Utilisée par _attach_help_main pour F1 / Shift+F1 / What's This.
    """
    mb = QMessageBox(window)
    mb.setWindowTitle("Aide")
    mb.setTextFormat(Qt.RichText)   # autorise balises HTML <b>, <ul>...
    mb.setIcon(QMessageBox.NoIcon)
    mb.setText(html)                # contenu HTML
    mb.setStandardButtons(QMessageBox.Ok)

    # On élargit le label interne pour éviter que le texte ne soit trop serré.
    lbl = mb.findChild(QLabel, "qt_msgbox_label")
    if lbl:
        lbl.setMinimumWidth(560)
        lbl.setWordWrap(True)

    mb.exec_()  # affichage modal


def _attach_help_main(window):
    """
    Connecte les raccourcis d'aide à la fenêtre principale :
      - F1 et Shift+F1 ouvrent la même boîte d'aide
      - Mode What's This (?) affiche aussi la même aide
    """

    def show():
        # Contenu HTML de l'aide de la fenêtre principale
        _show_help(window, """
        <h3>Gestionnaire d'Accès Réseau Local</h3>
        <ul>
          <li><b>Gestion</b> : gérer ou afficher les utilisateurs</li>
          <li><b>Outils</b> : hashage, générateur de mot de passe, chiffrement/déchiffrement</li>
          <li>Données : sauvegarde/chargement JSON</li>
        </ul>
        """)

    # Raccourci standard d'aide (F1)
    QShortcut(QKeySequence.HelpContents, window, activated=show)
    # Variante (Shift + F1) : ouvre la même aide
    QShortcut("Shift+F1", window, activated=show)

    # Filtre d'évènements : intercepte l'entrée en mode "What's This"
    class _HelpFilter(QtCore.QObject):
        def eventFilter(self, obj, ev):
            # Quand l'utilisateur active "What's This ?" (icône ? ou Shift+F1)
            if ev.type() == QtCore.QEvent.EnterWhatsThisMode:
                # On ne montre l'aide que si la fenêtre active est bien la fenêtre principale
                if QApplication.activeWindow() is window:
                    show()
                    QWhatsThis.leaveWhatsThisMode()  # quitter le mode pour éviter superposition
                    return True
            return False

    # Installer le filtre sur la fenêtre
    filt = _HelpFilter(window)
    window._helpFilter = filt                # on garde une référence pour éviter le GC
    window.installEventFilter(filt)

    # Afficher le bouton "?" dans la barre de titre si supporté par la plateforme
    try:
        window.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, True)
    except Exception:
        pass


def _pick_icon(*candidates):
    """
    Cherche une icône dans /Images parmi plusieurs noms candidats.
    Renvoie QIcon() si rien n'est trouvé (évite de planter).
    """
    for fname in candidates:
        p = os.path.join(BASE_DIR, "Images", fname)
        if os.path.exists(p):
            return QIcon(p)
    # Valeur par défaut
    p = os.path.join(BASE_DIR, "Images", "icone.png")
    return QIcon(p) if os.path.exists(p) else QIcon()


class FenetrePrincipale(QtWidgets.QMainWindow):
    """
    Fenêtre principale :
    - charge le .ui 'interface.ui'
    - applique le thème et le fond d'écran
    - ajuste la taille/position
    - connecte les actions de menu aux dialogues correspondants
    - instancie le gestionnaire de données (GestionnaireAcces)
    """

    def __init__(self):
        super().__init__()

        # 1) Charger l'UI construite dans Qt Designer
        uic.loadUi(os.path.join(BASE_DIR, 'interface.ui'), self)

        # 2) Appliquer le thème sombre + image de fond (Images/bg.jpg)
        apply_theme(self, os.path.join(BASE_DIR, 'Images', 'bg.jpg'))

        # 3) Définir l'icône de la fenêtre (si trouvé dans /Images)
        self.setWindowIcon(_pick_icon("icone.png"))

        # 4) Brancher l'aide (F1 / Shift+F1 / What's This)
        _attach_help_main(self)

        # 5) Contraintes de dimension min/max (16777215 = quasi "infini" pour Qt)
        self.setMinimumSize(100, 100)
        self.setMaximumSize(16777215, 16777215)

        # 6) Optionnel : desserrer la contrainte du layout central si présent
        cw = self.centralWidget()
        if cw and cw.layout():
            cw.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        # 7) Redimensionner la fenêtre à 90% de l'écran et la centrer
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        W, H = int(screen.width() * 0.9), int(screen.height() * 0.9)
        self.resize(W, H)
        self.move((screen.width() - W) // 2, (screen.height() - H) // 2)

        # 8) Créer l'instance du gestionnaire (source de vérité pour les utilisateurs)
        self.gestionnaire = GestionnaireAcces()

        # 9) Connecter les éléments de menu si le .ui les a définis (sécurité via hasattr)
        #    → Chaque action ouvre une boîte de dialogue correspondant à une fonctionnalité.

        # Menu Gestion → "Gestion d'utilisateurs"
        if hasattr(self, 'actionGestion_Utilisateurs'):
            self.actionGestion_Utilisateurs.triggered.connect(
                lambda: ouvrir_dialogue_gestion(self, self.gestionnaire)
            )

        # Menu Gestion → "Affichage d'utilisateurs"
        if hasattr(self, 'actionAffichage_Utilisateurs'):
            self.actionAffichage_Utilisateurs.triggered.connect(
                lambda: ouvrir_dialogue_affichage(self, self.gestionnaire)
            )

        # Menu Outils → "Hashage"
        if hasattr(self, 'actionHashage'):
            self.actionHashage.triggered.connect(lambda: ouvrir_dialogue_hash(self))

        # Menu Outils → "Générateur de MDP"
        if hasattr(self, 'actionGenerateur_MDP'):
            self.actionGenerateur_MDP.triggered.connect(lambda: ouvrir_dialogue_mdp(self))

        # Menu Outils → "Chiffrement / Déchiffrement (César)"
        if hasattr(self, 'actionChiffrement'):
            self.actionChiffrement.triggered.connect(lambda: ouvrir_dialogue_chiffrement(self))

        # Menu (souvent Fichier/Gestion) → "Quitter"
        if hasattr(self, 'actionQuitter'):
            self.actionQuitter.triggered.connect(QtWidgets.QApplication.instance().quit)


def main():
    """
    Création de l'application Qt, de la fenêtre principale, puis
    démarrage de la boucle d'évènements.
    """
    # 1) QApplication : obligatoire pour toute app Qt
    app = QtWidgets.QApplication(sys.argv)

    # 2) Icône d'application (affichée dans la barre des tâches, etc.)
    app.setWindowIcon(_pick_icon("icone.png", "icone.png"))

    # 3) Instanciation et affichage de la fenêtre principale
    fen = FenetrePrincipale()
    fen.show()

    # 4) Boucle événementielle Qt (bloquante jusqu'à fermeture)
    sys.exit(app.exec_())


if __name__ == '__main__':
    # Lancement direct : python main.py
    main()
