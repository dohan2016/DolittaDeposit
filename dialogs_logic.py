"""
dialogs_logic.py — Logique des boîtes de dialogue de l'application
- Regroupe l'ouverture et le comportement des fenêtres (Gestion, Affichage, Outils)
- Style unifié des popups
- Aide contextuelle (F1 / Shift+F1 / What's This)
- Helpers pour la taille des tableaux (répartition par pourcentages)
"""

import os, json, secrets, string, hashlib
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QFileDialog, QTableWidgetItem,
    QHeaderView, QAbstractScrollArea, QLayout, QSizePolicy,
    QApplication, QShortcut, QWhatsThis, QLabel
)
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import Qt
from theme import apply_theme

# Dossiers utiles (racine du projet + dossier contenant les .ui des dialogues)
BASE_DIR = os.path.dirname(__file__)
DIALOGS = os.path.join(BASE_DIR, 'dialogs')

# -------------------------------------------------------------------
# ---------     STYLE UNIFIÉ DES POPUPS (QMessageBox)     -----------
# -------------------------------------------------------------------
# On force un thème sombre, police lisible et boutons homogènes.
_POPUP_STYLESHEET = """
QMessageBox { background-color: rgba(16,17,23,238); border: 1px solid #2b2f36; }
QLabel#qt_msgbox_label {
    color: #f7faff; background: transparent; border: none;
    font-size: 18px; line-height: 1.4em; padding: 8px 6px;
}
QLabel#qt_msgboxex_icon_label, QLabel#qt_msgbox_icon_label { background: transparent; border: none; }
QPushButton {
    background: rgba(16,17,23,215); color: #e6edf3;
    border: 1px solid #2b2f36; border-radius: 8px; padding: 6px 14px; font-size: 15px;
}
QPushButton:hover { border-color: #3a88ff; }
"""
def _popup(parent, title, text, icon, extra_css=""):
    """
        Affiche un QMessageBox standard (OK) avec notre style.
        - parent : widget parent
        - title  : titre de la fenêtre
        - text   : message (plain text ou HTML basique)
        - icon   : type d'icône (Information / Warning / Critical / NoIcon)
        """
    mb = QMessageBox(parent)
    mb.setWindowTitle(title)
    mb.setIcon(icon)
    mb.setText(text)
    mb.setStandardButtons(QMessageBox.Ok)
    mb.setStyleSheet(_POPUP_STYLESHEET + extra_css)  # ← on ajoute un CSS spécifique si fourni
    lbl = mb.findChild(QLabel, "qt_msgbox_label")
    if lbl:
        lbl.setMinimumWidth(480)
        lbl.setWordWrap(True)
    mb.exec_()

def show_error(p, t, title='Erreur'):
    """Affiche un popup d'erreur (rouge)."""
    _popup(
        p, title, t, QMessageBox.Critical,
        extra_css="""
            QLabel#qt_msgbox_label {       /* texte principal */
                font-size: 20px;           /* ← +2px par rapport au style global (18px) */
            }
            QLabel#qt_msgbox_informativelabel {
                font-size: 18px; color: #cfd6e4;
            }
            QPushButton { font-size: 16px; }  /* boutons un poil plus grands aussi */
        """
    )


def show_info(p, t, title='Information'):
    """Affiche un popup d'information (bleu)."""
    _popup(p, title, t, QMessageBox.Information)

def show_warning(p, t, title='Attention'):
    """Affiche un popup d'avertissement (orange)."""
    _popup(p, title, t, QMessageBox.Warning)

def ask_confirm(parent, title, text, informative=''):
    """
    Affiche une boîte de confirmation Oui/Non (en FR) avec style sombre.
    - Utilisé, par ex., avant la suppression d'un utilisateur.

    NOTE : Pour agrandir le texte principal ici seulement, on peut concaténer
    un style supplémentaire (ex: font-size: 22px sur QLabel#qt_msgbox_label).
    """
    mb = QMessageBox(parent)
    mb.setWindowTitle(title)
    mb.setIcon(QMessageBox.Warning)
    mb.setText(text)
    if informative:
        mb.setInformativeText(informative)

    # Boutons Oui/Non en français (Windows affiche sinon Yes/No)
    mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    mb.button(QMessageBox.Yes).setText("Oui")
    mb.button(QMessageBox.No).setText("Non")

    # Par défaut : Non (principe de précaution)
    mb.setDefaultButton(QMessageBox.No)

    # Applique le style sombre cohérent
    mb.setStyleSheet(_POPUP_STYLESHEET)

    return mb.exec_() == QMessageBox.Yes

# -------------------------------------------------------------------
# ---------           DIALOGUE FICHIER JSON (I/O)         -----------
# -------------------------------------------------------------------
def _file_dialog(parent, mode='open'):
    """
    Ouvre une boîte de dialogue fichier (Qt non-native pour garder le style)
    - mode='open'  → sélection d'un fichier à ouvrir
    - mode='save'  → sauvegarde (on propose l'extension .json)
    Le fond est thémé via apply_theme(..., 'Images/gestion.jpg').
    """
    dlgFile = QFileDialog(parent)
    dlgFile.setOption(QFileDialog.DontUseNativeDialog, True)
    dlgFile.setAcceptMode(QFileDialog.AcceptSave if mode=='save' else QFileDialog.AcceptOpen)
    dlgFile.setNameFilter('JSON (*.json)')

    # Image de fond spécifique aux fenêtres "gestion"
    apply_theme(dlgFile, os.path.join(BASE_DIR, 'Images', 'gestion.jpg'))

    if dlgFile.exec_():
        return dlgFile.selectedFiles()[0]
    return ''

# -------------------------------------------------------------------
# ---------       HELPERS D'AJUSTEMENT DES TABLEAUX       ----------
# -------------------------------------------------------------------
def _prepare_table_fullwidth(table):
    """
    Prépare un QTableWidget :
    - Alternance de couleurs (lisibilité)
    - Politique d'ajustement : 'Interactive' sur toutes les colonnes
      → permet d'imposer ensuite une largeur au pixel près.
    - Pas de 'stretch last section' pour garder le contrôle.
    """
    table.setAlternatingRowColors(True)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)

    hdr = table.horizontalHeader()
    hdr.setMinimumSectionSize(80)
    hdr.setStretchLastSection(False)

    # On passe chaque section en 'Interactive' pour pouvoir fixer les largeurs
    for i in range(4):
        hdr.setSectionResizeMode(i, QHeaderView.Interactive)

def _install_adjust_columns_percent(
    table,
    ratios=(0.28, 0.42, 0.20, 0.10),  # largeurs relatives (Nom, Email, MDP, Actif) ; somme = 1.0
    mins=(140, 220, 220, 160)         # largeurs minimales (px) pour éviter l'écrasement du contenu
):
    """
    Installe un "auto-resize" des colonnes basé sur des pourcentages + minima.
    - Chaque redimensionnement de la table recalcule les largeurs
    - On réduit d'abord Email puis Nom si l'espace total manque, ensuite MDP puis Actif.
    """
    assert abs(sum(ratios) - 1.0) < 1e-6, "ratios must sum to 1.0"

    def adjust():
        # Largeur utile = largeur de la zone d'affichage du tableau
        vw = max(0, table.viewport().width())

        # Largeur cible par colonne = pourcentage * viewport, bornée par le min
        widths = [max(int(vw * r), m) for r, m in zip(ratios, mins)]

        # Si la somme dépasse la place disponible, on réduit progressivement
        total = sum(widths)
        if total > vw and vw > 0:
            overflow = total - vw

            # 1) Réduire Email
            cut_email = min(overflow, max(widths[1] - mins[1], 0)); widths[1] -= cut_email; overflow -= cut_email
            # 2) Puis Nom
            if overflow > 0:
                cut_nom = min(overflow, max(widths[0] - mins[0], 0)); widths[0] -= cut_nom; overflow -= cut_nom
            # 3) Puis MDP
            if overflow > 0:
                cut_mdp = min(overflow, max(widths[2] - mins[2], 0)); widths[2] -= cut_mdp; overflow -= cut_mdp
            # 4) Puis Actif
            if overflow > 0:
                cut_actif = min(overflow, max(widths[3] - mins[3], 0)); widths[3] -= cut_actif; overflow -= cut_actif

        # Application des largeurs
        for i, w in enumerate(widths):
            table.setColumnWidth(i, w)

    # Appel initial
    adjust()

    # On hooke l'event de resize du tableau pour recalculer à chaque fois
    orig_resize = getattr(table, "resizeEvent", None)

    def _on_resize(ev):
        try:
            if callable(orig_resize):
                orig_resize(ev)
        finally:
            adjust()

    table.resizeEvent = _on_resize
    return adjust  # renvoie le callback pour pouvoir le rappeler après un refresh

# -------------------------------------------------------------------
# ---------                   AIDE (F1, ?)                  ---------
# -------------------------------------------------------------------
def _show_help(dlg, html: str):
    """
    Petite boîte d'aide au format HTML (mode modal).
    """
    mb = QMessageBox(dlg)
    mb.setWindowTitle("Aide")
    mb.setTextFormat(Qt.RichText)
    mb.setIcon(QMessageBox.NoIcon)
    mb.setText(html)
    mb.setStandardButtons(QMessageBox.Ok)
    mb.setStyleSheet(_POPUP_STYLESHEET)

    lbl = mb.findChild(QLabel, "qt_msgbox_label")
    if lbl:
        lbl.setMinimumWidth(560)
        lbl.setWordWrap(True)

    mb.exec_()

def _attach_help(dlg, message_html: str):
    """
    Ajoute les raccourcis d'aide et le mode 'What's This' à un QDialog.
    - F1 et Shift+F1 → ouvrent la même aide HTML
    - Icône '?' (si supportée) → déclenche aussi la même aide
    """
    def show():
        _show_help(dlg, message_html)

    # Raccourcis clavier
    QShortcut(QKeySequence.HelpContents, dlg, activated=show)   # F1
    QShortcut(QKeySequence("Shift+F1"), dlg, activated=show)    # Shift+F1

    # Filtre d'événements pour capturer le mode "What's This ?"
    class _HelpFilter(QtCore.QObject):
        def __init__(self, owner, cb):
            super().__init__(owner)
            self.owner = owner
            self.cb = cb
        def eventFilter(self, obj, ev):
            if ev.type()==QtCore.QEvent.EnterWhatsThisMode and QApplication.activeWindow() is self.owner:
                self.cb()
                QWhatsThis.leaveWhatsThisMode()
                return True
            return False

    f = _HelpFilter(dlg, show)
    dlg._helpFilter = f               # garder une référence
    dlg.installEventFilter(f)

    # Affiche l'icône '?' dans la barre de titre si possible
    dlg.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, True)
    # Texte 'What's This ?' pour la fenêtre (si cliqué)
    dlg.setWhatsThis(message_html)

# ===================================================================
# ==============        DIALOGUE : GESTION (CRUD)        =============
# ===================================================================
def ouvrir_dialogue_gestion(parent, gestionnaire):
    """
    Ouvre la fenêtre 'gestion_utilisateurs.ui' :
    - Ajout / activation / désactivation / suppression
    - Filtre d'affichage (Tous/Actifs/Inactifs)
    - Export / import JSON
    - Tableau avec colonnes % (Nom/Email/MDP/Actif)
    """
    dlg = QDialog(parent)
    uic.loadUi(os.path.join(DIALOGS, 'gestion_utilisateurs.ui'), dlg)

    # Fond thémé
    apply_theme(dlg, os.path.join(BASE_DIR, 'Images', 'gestion.jpg'))

    # Aide contextuelle de cette fenêtre
    _attach_help(dlg, """
    <h3 style='font-size:22px;margin:0 0 6px 0;'>Gestion des utilisateurs</h3>
    <ul style='margin:0 0 0 18px;'>
      <li>Ajouter un utilisateur (Nom, Email)</li>
      <li>Activer/Désactiver la sélection</li>
      <li>Supprimer un utilisateur</li>
      <li>Filtrer par statut : Tous / Actifs / Inactifs</li>
      <li>Sauvegarder / Charger la base JSON</li>
    </ul>""")

    # Contraintes et centrage
    dlg.setMinimumSize(100,100)
    dlg.setMaximumSize(16777215,16777215)
    if dlg.layout():
        dlg.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
    screen = QApplication.primaryScreen().availableGeometry()
    W,H = int(screen.width()*0.7), int(screen.height()*0.7)
    dlg.resize(W,H)
    dlg.move((screen.width()-W)//2, (screen.height()-H)//2)

    # Si les layouts sont nommés dans le .ui, on peut ajuster leurs stretchs
    try:
        dlg.topLayout.setStretch(0,1)
        dlg.topLayout.setStretch(1,1)
        dlg.topLayout.setStretch(2,0)
        dlg.filterLayout.setStretch(0,1)
        dlg.filterLayout.setStretch(1,1)
        dlg.filterLayout.setStretch(2,1)
    except Exception:
        pass

    # Préparation du tableau (lecture seule, sélection par ligne)
    table = dlg.table
    table.setEditTriggers(table.NoEditTriggers)
    table.setSelectionBehavior(table.SelectRows)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Colonnes "à pourcentage" (28/42/20/10) + minima
    _prepare_table_fullwidth(table)
    adjust = _install_adjust_columns_percent(
        table,
        ratios=(0.28, 0.42, 0.20, 0.10),
        mins=(140, 220, 220, 160)
    )

    def refresh_table():
        """
        Recharge les données depuis le gestionnaire,
        remplit la table, puis recalcule les largeurs.
        """
        users = gestionnaire.lister_utilisateurs(dlg.comboFiltre.currentText())
        table.setRowCount(len(users))
        for r,u in enumerate(users):
            table.setItem(r,0, QTableWidgetItem(u['nom']))
            table.setItem(r,1, QTableWidgetItem(u['email']))
            table.setItem(r,2, QTableWidgetItem(u['mot_de_passe']))
            table.setItem(r,3, QTableWidgetItem('Oui' if u['actif'] else 'Non'))
        adjust()  # remet les colonnes à la bonne taille (viewport actuel)

    # Filtre : au changement, on recharge
    dlg.comboFiltre.currentIndexChanged.connect(refresh_table)

    def add_user():
        """Ajoute un utilisateur (Nom/Email) puis refresh."""
        nom = dlg.inputNom.text().strip()
        email = dlg.inputEmail.text().strip()
        try:
            gestionnaire.ajouter_utilisateur(nom, email)
            dlg.inputNom.clear()
            dlg.inputEmail.clear()
            refresh_table()
        except Exception as e:
            show_error(dlg, str(e))

    def activer(sel=True):
        """Active/Désactive l'utilisateur de la ligne sélectionnée."""
        row = table.currentRow()
        if row < 0:
            return show_error(dlg, 'Sélectionnez une ligne.')
        email = table.item(row,1).text()
        try:
            gestionnaire.activer(email) if sel else gestionnaire.desactiver(email)
            refresh_table()
        except Exception as e:
            show_error(dlg, str(e))

    def supprimer():
        """
        Demande confirmation puis supprime l'utilisateur sélectionné.
        - Affiche le nom et l'email dans le message de confirmation.
        """
        row = table.currentRow()
        if row < 0:
            return show_error(dlg, 'Sélectionnez une ligne.')
        nom   = table.item(row, 0).text()
        email = table.item(row, 1).text()

        # Confirmation Oui/Non (FR)
        if not ask_confirm(
            dlg,
            'Confirmation de suppression',
            "Voulez-vous vraiment supprimer cet utilisateur ?",
            f"Nom : {nom}\nEmail : {email}"
        ):
            return  # Annulé

        try:
            gestionnaire.supprimer_utilisateur(email)
            refresh_table()
            show_info(dlg, "Utilisateur supprimé.")
        except Exception as e:
            show_error(dlg, str(e))

    def sauvegarder():
        """
        Exporte la base en JSON.
        - Garde-fou : refuse d'exporter si la table est vide.
        - Ajoute .json si l'utilisateur n'a pas mis d'extension.
        """
        if table.rowCount() == 0:
            return show_warning(
                dlg,
                "Aucune donnée à sauvegarder.\nAjoutez au moins un utilisateur avant d'exporter.",
                "Sauvegarde"
            )
        path = _file_dialog(dlg,'save')
        if path:
            if not path.lower().endswith('.json'):
                path += '.json'
            try:
                gestionnaire.sauvegarder(path)
                show_info(dlg,'Fichier JSON sauvegardé avec succès.','Sauvegarde')
            except Exception as e:
                show_error(dlg, str(e))

    def charger():
        """
        Importe un JSON et recharge la table.
        - Positionne le filtre sur 'Tous' après import.
        """
        path = _file_dialog(dlg,'open')
        if path:
            try:
                n = gestionnaire.charger(path)
                dlg.comboFiltre.setCurrentText('Tous')
                refresh_table()
                show_info(dlg, f'{n} utilisateur(s) chargé(s).', 'Chargement')
            except Exception as e:
                show_error(dlg, f'Echec de chargement: {e}')

    # Connexions des boutons
    dlg.btnAjouter.clicked.connect(add_user)
    dlg.btnActiver.clicked.connect(lambda: activer(True))
    dlg.btnDesactiver.clicked.connect(lambda: activer(False))
    dlg.btnSupprimer.clicked.connect(supprimer)
    dlg.btnSauvegarder.clicked.connect(sauvegarder)
    dlg.btnCharger.clicked.connect(charger)
    dlg.btnFermer.clicked.connect(dlg.close)

    # Affichage initial
    refresh_table()
    dlg.exec_()

# ===================================================================
# ==============             OUTILS DIVERS               =============
# ===================================================================
def ouvrir_dialogue_hash(parent):
    """
    Ouvre 'hash.ui' : calcule l'empreinte (hex) d'un texte selon l'algo choisi.
    """
    dlg = QDialog(parent)
    uic.loadUi(os.path.join(DIALOGS, 'hash.ui'), dlg)
    apply_theme(dlg, os.path.join(BASE_DIR, 'Images', 'cyber.jpg'))

    # Aide dédiée
    _attach_help(dlg, """
    <h3 style='font-size:22px;margin:0 0 6px 0;'>Hashage de texte</h3>
    <ul style='margin:0 0 0 18px;'>
      <li>Saisissez le texte librement</li>
      <li>Choisissez l'algorithme (SHA256, SHA1, MD5)</li>
      <li>Cliquez sur <em>Hacher</em> pour obtenir l'empreinte hexadécimale</li>
    </ul>""")

    # Contraintes + centrage
    dlg.setMinimumSize(100,100)
    dlg.setMaximumSize(16777215,16777215)
    if dlg.layout():
        dlg.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
    screen = QApplication.primaryScreen().availableGeometry()
    W,H = int(screen.width()*0.7), int(screen.height()*0.7)
    dlg.resize(W,H)
    dlg.move((screen.width()-W)//2, (screen.height()-H)//2)

    def do_hash():
        # Récupérer le texte brut (sans encodage d'abord)
        raw = dlg.inputTexte.toPlainText()
        if not raw.strip():
            show_error(dlg, "Veuillez saisir du texte à hacher.")
            dlg.inputTexte.setFocus()
            return

        texte = raw.encode('utf-8')
        algo = dlg.comboAlgo.currentText().lower()
        try:
            dlg.outputHash.setText(getattr(hashlib, algo)(texte).hexdigest())
        except Exception as e:
            show_error(dlg, f'Erreur de hashage: {e}')

    dlg.btnHasher.clicked.connect(do_hash)
    dlg.btnFermer.clicked.connect(dlg.close)
    dlg.exec_()

def ouvrir_dialogue_mdp(parent):
    """
    Ouvre 'generateur_mdp.ui' : génère un mot de passe aléatoire selon
    les catégories cochées (Maj/Min/Chiffres/Symboles) et la longueur.
    """
    dlg = QDialog(parent)
    uic.loadUi(os.path.join(DIALOGS, 'generateur_mdp.ui'), dlg)
    apply_theme(dlg, os.path.join(BASE_DIR, 'Images', 'cyber.jpg'))

    # Aide dédiée
    _attach_help(dlg, """
    <h3 style='font-size:22px;margin:0 0 6px 0;'>Générateur de mot de passe</h3>
    <ul style='margin:0 0 0 18px;'>
      <li>Cochez les catégories (Maj/Min/Chiffres/Symboles)</li>
      <li>Choisissez la longueur</li>
      <li>Cliquez sur <em>Générer</em> pour produire un MDP aléatoire</li>
    </ul>""")

    # Contraintes + centrage
    dlg.setMinimumSize(100,100)
    dlg.setMaximumSize(16777215,16777215)
    if dlg.layout():
        dlg.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
    screen = QApplication.primaryScreen().availableGeometry()
    W,H = int(screen.width()*0.7), int(screen.height()*0.7)
    dlg.resize(W,H)
    dlg.move((screen.width()-W)//2, (screen.height()-H)//2)

    def generer():
        """Compose l'alphabet puis fabrique un MDP aléatoire de longueur choisie."""
        choix = ''
        if dlg.chkMaj.isChecked():      choix += string.ascii_uppercase
        if dlg.chkMin.isChecked():      choix += string.ascii_lowercase
        if dlg.chkChiffres.isChecked(): choix += string.digits
        if dlg.chkSymboles.isChecked(): choix += '!@#$%^&*()-_=+[]{};:,.?/'
        if not choix:
            return show_error(dlg, 'Sélectionnez au moins une catégorie de caractères.')
        lg = dlg.spinLongueur.value()
        dlg.outputMDP.setText(''.join(secrets.choice(choix) for _ in range(lg)))

    dlg.btnGenerer.clicked.connect(generer)
    dlg.btnFermer.clicked.connect(dlg.close)
    dlg.exec_()

# Petit algo de chiffrement "César" (démo pédagogique)
def _caesar(text, shift, decrypt=False):
    """
    Chiffre/Déchiffre un texte par décalage de lettres.
    - shift : valeur de décalage (0–25)
    - decrypt=True → décale en sens inverse
    """
    out = []
    shift = (-shift) % 26 if decrypt else shift
    for ch in text:
        if ch.isalpha():
            base = 'A' if ch.isupper() else 'a'
            base_ord = ord(base)
            out.append(chr((ord(ch)-base_ord+shift) % 26 + base_ord))
        else:
            out.append(ch)
    return ''.join(out)

def ouvrir_dialogue_chiffrement(parent):
    """
    Ouvre 'chiffrement.ui' :
    - Saisie du texte
    - Choix du mode (Chiffrer / Déchiffrer) et du décalage
    - Affiche le résultat dans la zone de sortie
    """
    dlg = QDialog(parent)
    uic.loadUi(os.path.join(DIALOGS, 'chiffrement.ui'), dlg)
    apply_theme(dlg, os.path.join(BASE_DIR, 'Images', 'cyber.jpg'))

    # Aide dédiée
    _attach_help(dlg, """
    <h3 style='font-size:22px;margin:0 0 6px 0;'>Chiffrement / Déchiffrement (César)</h3>
    <ul style='margin:0 0 0 18px;'>
      <li>Saisissez le texte</li>
      <li>Choisissez le mode (Chiffrer / Déchiffrer) et le décalage (0–25)</li>
      <li>Cliquez sur <em>Exécuter</em> pour obtenir le résultat</li>
    </ul>""")

    # Contraintes + centrage
    dlg.setMinimumSize(100,100)
    dlg.setMaximumSize(16777215,16777215)
    if dlg.layout():
        dlg.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
    screen = QApplication.primaryScreen().availableGeometry()
    W,H = int(screen.width()*0.7), int(screen.height()*0.7)
    dlg.resize(W,H)
    dlg.move((screen.width()-W)//2, (screen.height()-H)//2)

    def run():
        raw = dlg.inputTexte.toPlainText()
        if not raw.strip():
            show_error(dlg, "Veuillez saisir du texte à traiter (chiffrer / déchiffrer).")
            dlg.inputTexte.setFocus()
            return

        shift = dlg.spinDecalage.value()
        mode = dlg.comboMode.currentText()
        try:
            dlg.outputTexte.setPlainText(_caesar(raw, shift, decrypt=(mode == 'Déchiffrer')))
        except Exception as e:
            show_error(dlg, f"Erreur pendant le traitement: {e}")

    dlg.btnExecuter.clicked.connect(run)
    dlg.btnFermer.clicked.connect(dlg.close)
    dlg.exec_()

# ===================================================================
# ==============    DIALOGUE : AFFICHAGE (READ-ONLY)     =============
# ===================================================================
def ouvrir_dialogue_affichage(parent, gestionnaire):
    """
    Ouvre 'affichage_utilisateurs.ui' en lecture seule :
    - Filtre Tous / Actifs / Inactifs
    - Tableau non modifiable, même logique d'ajustement des colonnes
    """
    dlg = QDialog(parent)
    uic.loadUi(os.path.join(DIALOGS, 'affichage_utilisateurs.ui'), dlg)
    apply_theme(dlg, os.path.join(BASE_DIR, 'Images', 'gestion.jpg'))

    # Aide dédiée
    _attach_help(dlg, """
    <h3 style='font-size:22px;margin:0 0 6px 0;'>Affichage des utilisateurs (lecture seule)</h3>
    <ul style='margin:0 0 0 18px;'>
      <li>Utilisez le filtre : Tous / Actifs / Inactifs</li>
      <li>Cliquez sur <em>Actualiser</em> pour mettre à jour la liste</li>
      <li>Aucune modification n'est possible ici</li>
    </ul>""")

    # Contraintes + centrage
    dlg.setMinimumSize(100,100)
    dlg.setMaximumSize(16777215,16777215)
    if dlg.layout():
        dlg.layout().setSizeConstraint(QLayout.SetDefaultConstraint)
    screen = QApplication.primaryScreen().availableGeometry()
    W,H = int(screen.width()*0.7), int(screen.height()*0.7)
    dlg.resize(W,H)
    dlg.move((screen.width()-W)//2, (screen.height()-H)//2)

    # Tableau lecture seule + ajustement colonnes
    table = dlg.table
    table.setEditTriggers(table.NoEditTriggers)
    table.setSelectionBehavior(table.SelectRows)

    _prepare_table_fullwidth(table)
    adjust = _install_adjust_columns_percent(
        table,
        ratios=(0.28, 0.42, 0.20, 0.10),
        mins=(140, 220, 220, 160)
    )

    def refresh_table():
        """Recharge la liste selon le filtre courant, puis ajuste les colonnes."""
        users = gestionnaire.lister_utilisateurs(dlg.comboFiltre.currentText())
        table.setRowCount(len(users))
        for r,u in enumerate(users):
            table.setItem(r,0, QTableWidgetItem(u['nom']))
            table.setItem(r,1, QTableWidgetItem(u['email']))
            table.setItem(r,2, QTableWidgetItem(u['mot_de_passe']))
            table.setItem(r,3, QTableWidgetItem('Oui' if u['actif'] else 'Non'))
        adjust()

    dlg.comboFiltre.currentIndexChanged.connect(refresh_table)
    dlg.btnActualiser.clicked.connect(refresh_table)
    dlg.btnFermer.clicked.connect(dlg.close)

    refresh_table()
    dlg.exec_()
