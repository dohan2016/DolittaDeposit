import tkinter as tk
from tkinter import ttk

def afficher_explanation(event):
    choix = combo.get()
    explications = {
        "Public": "Aucune restriction",
        "Confidentiel": "Accès restreint au personnel autorisé",
        "Très Secret": "Accès limité, autorisation spéciale requise"
    }

    # Effacer le contenu actuel de la zone de texte
    texte.delete("1.0", tk.END)
    # Insérer la nouvelle explication
    texte.insert(tk.END, explications.get(choix, ""))

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Classification des documents")
fenetre.geometry("350x200")

# Label d'instruction
label = tk.Label(fenetre, text="Sélectionnez un niveau de confidentialité :", font=("Arial", 11))
label.pack(pady=10)

# Combobox
combo = ttk.Combobox(fenetre, values=["Public", "Confidentiel", "Très Secret"], state="readonly")
combo.pack()
combo.bind("<<ComboboxSelected>>", afficher_explanation)

# Zone de texte pour l’explication
texte = tk.Text(fenetre, height=4, width=40)
texte.pack(pady=10)

# Lancement de l'application
fenetre.mainloop()
