from PyQt5 import QtWidgets
from interface import Ui_MainWindow
from hashage_dialog import Ui_Dialog as Ui_Hashage
from mdp_dialog import Ui_Dialog as Ui_MDP
from chiffrement_dialog import Ui_Dialog as Ui_Chiffrement
from outils.chiffrement import chiffrer_cesar, dechiffrer_cesar, chiffrer_aes, dechiffrer_aes
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QTableWidgetItem


from modules.Utilisateur import Utilisateur
from modules.GestionnaireAcces import GestionnaireAcces
from outils.hashage import hasher_texte
from outils.mot_de_passe import generer_mot_de_passe

class FenetrePrincipale(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("icone.png"))
        self.ajouter_filtre_statut()
        # Fixer la taille de la fenêtre principale
        self.setFixedSize(840,800)

        self.gestionnaire = GestionnaireAcces()
        self.fichier_json = "sauvegarde.json"

        # Définir les colonnes du tableau
        self.ui.tableWidget_utilisateurs.setColumnCount(4)
        self.ui.tableWidget_utilisateurs.setHorizontalHeaderLabels(["Nom", "Email", "Mot de passe", "Actif"])

        # Connexions des boutons
        self.ui.pushButton_ajouter.clicked.connect(self.ajouter_utilisateur)
        self.ui.pushButton_supprimer.clicked.connect(self.supprimer_utilisateur)
        self.ui.pushButton_activer.clicked.connect(lambda: self.changer_statut(True))
        self.ui.pushButton_desactiver.clicked.connect(lambda: self.changer_statut(False))
        self.ui.pushButton_sauvegarder.clicked.connect(self.sauvegarder)
        self.ui.pushButton_charger.clicked.connect(self.charger)

        # Menu Outils
        self.ui.actionHashage.triggered.connect(self.ouvrir_hashage)
        self.ui.actionMotDePasse.triggered.connect(self.ouvrir_mdp)
        self.ui.actionChiffrement.triggered.connect(self.ouvrir_chiffrement)

    def ouvrir_chiffrement(self):
        dialog = QtWidgets.QDialog(self)
        ui = Ui_Chiffrement()
        ui.setupUi(dialog)

        def executer():
            texte = ui.lineEdit_texte.text()
            cle = ui.lineEdit_cle.text()
            algo = ui.comboBox_algo.currentText()
            mode = "chiffrer" if ui.radioButton_chiffrer.isChecked() else "dechiffrer"

            if algo == "César":
                resultat = chiffrer_cesar(texte, cle) if mode == "chiffrer" else dechiffrer_cesar(texte, cle)
            elif algo == "AES":
                resultat = chiffrer_aes(texte, cle) if mode == "chiffrer" else dechiffrer_aes(texte, cle)
            else:
                resultat = "Algorithme inconnu"

            ui.textEdit_resultat.setPlainText(resultat)

        ui.pushButton_exec.clicked.connect(executer)
        dialog.exec_()

    def ajouter_filtre_statut(self):
        """Ajoute un menu déroulant (comboBox) pour filtrer les utilisateurs."""
        self.comboBox_filtre = QComboBox()
        self.comboBox_filtre.addItems(["Tous", "Actifs", "Inactifs"])
        self.comboBox_filtre.currentIndexChanged.connect(self.filtrer_utilisateurs)

        # Ajoute le comboBox en haut de la fenêtre (si layout vertical)
        self.ui.verticalLayout.insertWidget(0, self.comboBox_filtre)

    def ajouter_utilisateur_dans_table(self, utilisateur):
        row = self.ui.tableWidget_utilisateurs.rowCount()
        self.ui.tableWidget_utilisateurs.insertRow(row)
        self.ui.tableWidget_utilisateurs.setItem(row, 0, QTableWidgetItem(utilisateur.nom))
        self.ui.tableWidget_utilisateurs.setItem(row, 1, QTableWidgetItem(utilisateur.email))
        self.ui.tableWidget_utilisateurs.setItem(row, 2, QTableWidgetItem(utilisateur.mot_de_passe))
        self.ui.tableWidget_utilisateurs.setItem(row, 3, QTableWidgetItem("Oui" if utilisateur.actif else "Non"))

    def filtrer_utilisateurs(self):
        """Filtre les lignes du tableau en fonction du statut sélectionné."""
        filtre = self.comboBox_filtre.currentText()
        self.ui.tableWidget_utilisateurs.setRowCount(0)  # Vide le tableau

        for utilisateur in self.gestionnaire.utilisateurs:
            afficher = (
                    filtre == "Tous" or
                    (filtre == "Actifs" and utilisateur.actif) or
                    (filtre == "Inactifs" and not utilisateur.actif)
            )
            if afficher:
                self.ajouter_utilisateur_dans_table(utilisateur)

    def ajouter_utilisateur(self):
        nom = self.ui.lineEdit_nom.text().strip()
        email = self.ui.lineEdit_email.text().strip()
        if nom and email:
            mdp = self.gestionnaire.generer_mot_de_passe()
            utilisateur = Utilisateur(nom, email, mdp)
            self.gestionnaire.ajouter_utilisateur(utilisateur)
            self.ui.lineEdit_nom.clear()
            self.ui.lineEdit_email.clear()
            self.actualiser_tableau()

    def actualiser_tableau(self):
        self.ui.tableWidget_utilisateurs.setRowCount(0)
        for utilisateur in self.gestionnaire.utilisateurs:
            row = self.ui.tableWidget_utilisateurs.rowCount()
            self.ui.tableWidget_utilisateurs.insertRow(row)
            self.ui.tableWidget_utilisateurs.setItem(row, 0, QtWidgets.QTableWidgetItem(utilisateur.nom))
            self.ui.tableWidget_utilisateurs.setItem(row, 1, QtWidgets.QTableWidgetItem(utilisateur.email))
            self.ui.tableWidget_utilisateurs.setItem(row, 2, QtWidgets.QTableWidgetItem(utilisateur.mot_de_passe))
            self.ui.tableWidget_utilisateurs.setItem(row, 3, QtWidgets.QTableWidgetItem("Oui" if utilisateur.actif else "Non"))

    def get_email_selectionne(self):
        row = self.ui.tableWidget_utilisateurs.currentRow()
        if row >= 0:
            item = self.ui.tableWidget_utilisateurs.item(row, 1)  # Colonne email
            if item:
                return item.text()
        return None

    def supprimer_utilisateur(self):
        email = self.get_email_selectionne()
        if email:
            self.gestionnaire.supprimer_utilisateur(email)
            self.actualiser_tableau()

    def changer_statut(self, activer=True):
        email = self.get_email_selectionne()
        utilisateur = self.gestionnaire.get_utilisateur(email)
        if utilisateur:
            utilisateur.activer() if activer else utilisateur.desactiver()
            self.actualiser_tableau()

    def sauvegarder(self):
        self.gestionnaire.sauvegarder_json(self.fichier_json)

    def charger(self):
        self.gestionnaire.charger_json(self.fichier_json)
        self.actualiser_tableau()

    def ouvrir_hashage(self):
        dialog = QtWidgets.QDialog(self)
        ui = Ui_Hashage()
        ui.setupUi(dialog)
        ui.comboBox_algorithme.addItems(["md5", "sha1", "sha256", "sha512"])

        def hasher():
            texte = ui.lineEdit_texte.text()
            algo = ui.comboBox_algorithme.currentText()
            resultat = hasher_texte(texte, algo)
            ui.textEdit_resultat.setPlainText(resultat)

        ui.pushButton_hasher.clicked.connect(hasher)
        dialog.exec_()

    def ouvrir_mdp(self):
        dialog = QtWidgets.QDialog(self)
        ui = Ui_MDP()
        ui.setupUi(dialog)

        def generer():
            longueur = ui.spinBox_longueur.value()
            motdepasse = generer_mot_de_passe(longueur)
            ui.lineEdit_resultat.setText(motdepasse)

        ui.pushButton_generer.clicked.connect(generer)
        dialog.exec_()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())
