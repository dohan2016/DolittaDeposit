import tkinter as tk
from tkinter import messagebox, ttk
from gestion_acces import GestionnaireAcces

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestionnaire d'accès réseau local")
        self.geometry("700x500")
        self.gestionnaire = GestionnaireAcces()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        frame_form = tk.Frame(self)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="Nom:").grid(row=0, column=0)
        self.entry_nom = tk.Entry(frame_form)
        self.entry_nom.grid(row=0, column=1)

        tk.Label(frame_form, text="Email:").grid(row=0, column=2)
        self.entry_email = tk.Entry(frame_form)
        self.entry_email.grid(row=0, column=3)

        btn_ajouter = tk.Button(frame_form, text="Ajouter utilisateur", command=self.ajouter_utilisateur)
        btn_ajouter.grid(row=0, column=4, padx=10)

        frame_actions = tk.Frame(self)
        frame_actions.pack(pady=10)

        btn_sauvegarder = tk.Button(frame_actions, text="Sauvegarder JSON", command=self.sauvegarder)
        btn_sauvegarder.pack(side=tk.LEFT, padx=5)

        btn_charger = tk.Button(frame_actions, text="Charger JSON", command=self.charger)
        btn_charger.pack(side=tk.LEFT, padx=5)

        self.filtre_var = tk.StringVar(value="Tous")
        filtre_menu = ttk.Combobox(frame_actions, textvariable=self.filtre_var, values=["Tous", "Actifs", "Inactifs"], state="readonly", width=10)
        filtre_menu.pack(side=tk.RIGHT, padx=10)
        filtre_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        columns = ("nom", "email", "statut", "actions")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.heading("nom", text="Nom")
        self.tree.heading("email", text="Email")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("actions", text="Action")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.toggle_statut_ou_supprimer)

    def ajouter_utilisateur(self):
        nom = self.entry_nom.get().strip()
        email = self.entry_email.get().strip()

        if not nom or not email:
            messagebox.showwarning("Champs vides", "Nom et Email sont requis.")
            return

        if self.gestionnaire.get_utilisateur(email):
            messagebox.showwarning("Erreur", "Utilisateur déjà existant.")
            return

        self.gestionnaire.ajouter_utilisateur(nom, email)
        self.entry_nom.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.refresh_table()

    def toggle_statut_ou_supprimer(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item)
        email = item["values"][1]
        utilisateur = self.gestionnaire.get_utilisateur(email)

        action = messagebox.askquestion("Action", "Souhaitez-vous activer/désactiver ce compte ?\nSinon, cliquez sur 'Non' pour le supprimer.")
        if action == 'yes':
            if utilisateur.actif:
                utilisateur.desactiver()
            else:
                utilisateur.activer()
        else:
            self.gestionnaire.supprimer_utilisateur(email)

        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtre = self.filtre_var.get()
        for u in self.gestionnaire.utilisateurs:
            if filtre == "Actifs" and not u.actif:
                continue
            elif filtre == "Inactifs" and u.actif:
                continue
            statut = "Actif" if u.actif else "Inactif"
            self.tree.insert("", "end", values=(u.nom, u.email, statut, "Double-cliquer"))

    def sauvegarder(self):
        self.gestionnaire.sauvegarder_json("utilisateurs.json")
        messagebox.showinfo("Sauvegarde", "Données sauvegardées avec succès.")

    def charger(self):
        self.gestionnaire.charger_json("utilisateurs.json")
        self.refresh_table()
        messagebox.showinfo("Chargement", "Données chargées avec succès.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
