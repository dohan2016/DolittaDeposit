import os, sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QShortcut, QLabel, QApplication, QWhatsThis
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt

from theme import apply_theme
from dialogs_logic import (
    ouvrir_dialogue_gestion,
    ouvrir_dialogue_hash,
    ouvrir_dialogue_mdp,
    ouvrir_dialogue_chiffrement,
    ouvrir_dialogue_affichage,
)
from modules.gestionnaire_acces import GestionnaireAcces

BASE_DIR = os.path.dirname(__file__)

def _show_help(window, html):
    mb = QMessageBox(window)
    mb.setWindowTitle("Aide")
    mb.setTextFormat(Qt.RichText)
    mb.setIcon(QMessageBox.NoIcon)
    mb.setText(html)
    mb.setStandardButtons(QMessageBox.Ok)
    lbl = mb.findChild(QLabel, "qt_msgbox_label")
    if lbl:
        lbl.setMinimumWidth(560)
        lbl.setWordWrap(True)
    mb.exec_()

def _attach_help_main(window):
    def show():
        _show_help(window, """
        <h3>Gestionnaire d'Accès Réseau Local</h3>
        <ul>
          <li><b>Gestion</b> : gérer ou afficher les utilisateurs</li>
          <li><b>Outils</b> : hashage, générateur de mot de passe, chiffrement/déchiffrement</li>
          <li>Données : sauvegarde/chargement JSON</li>
        </ul>
        """)
    QShortcut(QKeySequence.HelpContents, window, activated=show)
    QShortcut("Shift+F1", window, activated=show)

    class _HelpFilter(QtCore.QObject):
        def eventFilter(self, obj, ev):
            if ev.type() == QtCore.QEvent.EnterWhatsThisMode:
                if QApplication.activeWindow() is window:
                    show(); QWhatsThis.leaveWhatsThisMode(); return True
            return False
    filt = _HelpFilter(window)
    window._helpFilter = filt
    window.installEventFilter(filt)
    try:
        window.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, True)
    except Exception:
        pass

__version__ = "1.0.0"

_ABOUT_CSS = """
QMessageBox { background-color: rgba(16,17,23,238); border: 1px solid #2b2f36; }
QLabel#qt_msgbox_label {
    color: #f7faff; background: transparent; border: none;
    font-size: 18px; line-height: 1.4em; padding: 8px 6px;
}
QPushButton {
    background: rgba(16,17,23,215); color: #e6edf3;
    border: 1px solid #2b2f36; border-radius: 8px; padding: 6px 14px; font-size: 15px;
}
QPushButton:hover { border-color: #3a88ff; }
"""

def _show_about(window):
    html = f"""
    <h3 style='margin:0 0 8px 0;'>Gestionnaire d'Accès Réseau Local</h3>
    <ul style='margin:0 0 8px 22px;'>
      <li>Gestion des utilisateurs (CRUD, filtres, JSON)</li>
      <li>Outils cybersécurité : Hashage, Générateur MDP, Chiffrement César</li>
    </ul>
    <p style='margin:0;color:#cfd8e3;'>
      Réalisée par : <b>Dounia Hanbali</b> 
    </p>
    <p style='margin:0 0 8px 0;color:#cfd8e3;'>Version {__version__}</p>
    """
    mb = QMessageBox(window)
    mb.setWindowTitle("À propos")
    mb.setTextFormat(Qt.RichText)
    mb.setIcon(QMessageBox.Information)
    mb.setText(html)
    mb.setStandardButtons(QMessageBox.Ok)
    mb.setStyleSheet(_ABOUT_CSS)
    mb.setWindowIcon(window.windowIcon())
    lbl = mb.findChild(QLabel, "qt_msgbox_label")
    if lbl:
        lbl.setMinimumWidth(520); lbl.setWordWrap(True)
    mb.exec_()

def _pick_icon(*candidates):
    for fname in candidates:
        p = os.path.join(BASE_DIR, "Images", fname)
        if os.path.exists(p): return QIcon(p)
    p = os.path.join(BASE_DIR, "Images", "icone.png")
    return QIcon(p) if os.path.exists(p) else QIcon()

class FenetrePrincipale(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(BASE_DIR, 'interface.ui'), self)
        apply_theme(self, os.path.join(BASE_DIR, 'Images', 'bg.jpg'))
        self.setWindowIcon(_pick_icon("icone.png"))
        _attach_help_main(self)

        self.setMinimumSize(100, 100); self.setMaximumSize(16777215, 16777215)
        cw = self.centralWidget()
        if cw and cw.layout():
            cw.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        W, H = int(screen.width()*0.9), int(screen.height()*0.9)
        self.resize(W, H); self.move((screen.width()-W)//2, (screen.height()-H)//2)

        self.gestionnaire = GestionnaireAcces()

        # Menus Gestion / Outils (du .ui)
        if hasattr(self, 'actionGestion_Utilisateurs'):
            self.actionGestion_Utilisateurs.triggered.connect(
                lambda: ouvrir_dialogue_gestion(self, self.gestionnaire))
        if hasattr(self, 'actionAffichage_Utilisateurs'):
            self.actionAffichage_Utilisateurs.triggered.connect(
                lambda: ouvrir_dialogue_affichage(self, self.gestionnaire))
        if hasattr(self, 'actionHashage'):
            self.actionHashage.triggered.connect(lambda: ouvrir_dialogue_hash(self))
        if hasattr(self, 'actionGenerateur_MDP'):
            self.actionGenerateur_MDP.triggered.connect(lambda: ouvrir_dialogue_mdp(self))
        if hasattr(self, 'actionChiffrement'):
            self.actionChiffrement.triggered.connect(lambda: ouvrir_dialogue_chiffrement(self))
        if hasattr(self, 'actionQuitter'):
            self.actionQuitter.triggered.connect(QtWidgets.QApplication.instance().quit)

        # ===== À PROPOS en un clic (action directe sur la barre de menu) =====
        menubar = self.menuBar()

        # (Optionnel) supprimer un éventuel menu "À propos" existant (sous-menu) pour éviter le double clic
        for m in menubar.findChildren(QtWidgets.QMenu):
            if m.title() in ("À propos", "A propos", "&À propos", "&A propos"):
                menubar.removeAction(m.menuAction())
                m.deleteLater()
                break

        # Ajoute une action directement dans la barre de menu (pas de sous-menu)
        action_apropos_bar = menubar.addAction("À propos")
        action_apropos_bar.triggered.connect(lambda: _show_about(self))

        # Si ton .ui contient déjà une action 'actionA_Propos', on la branche aussi (au cas où)
        if hasattr(self, "actionA_Propos"):
            self.actionA_Propos.triggered.connect(lambda: _show_about(self))

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(_pick_icon("icone.png", "icone.png"))
    fen = FenetrePrincipale()
    fen.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
