import tkinter as tk

def afficher_message():
    nom = entree_nom.get().strip()
    if nom:
        message = f"Bonjour, {nom} ! Bienvenue dans le monde de la cybersécurité."
        label_message.config(text=message)
    else:
        label_message.config(text="Veuillez entrer votre nom.")

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Bienvenue en cybersécurité")
fenetre.geometry("600x300")

# Champ de saisie
label_nom = tk.Label(fenetre, text="Entrez votre nom :")
label_nom.pack(pady=5)

entree_nom = tk.Entry(fenetre, width=30)
entree_nom.pack(pady=5)

# Bouton Afficher
bouton = tk.Button(fenetre, text="Afficher", command=afficher_message)
bouton.pack(pady=10)

# Label pour le message de bienvenue
label_message = tk.Label(fenetre, text="", font=("Arial", 11), fg="blue")
label_message.pack(pady=10)

# Lancer l'application
fenetre.mainloop()
