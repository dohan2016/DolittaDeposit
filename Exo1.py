import tkinter as tk

def afficher_selection():
    # Récupère les indices sélectionnés
    selections = listbox.curselection()
    # Affiche les éléments sélectionnés
    for i in selections:
        print(listbox.get(i))

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Concepts de Cybersécurité")
fenetre.geometry("300x250")

# Titre
label = tk.Label(fenetre, text="Sélectionnez les concepts :", font=("Arial", 12))
label.pack(pady=10)

# Création de la Listbox avec sélection multiple
listbox = tk.Listbox(fenetre, selectmode=tk.MULTIPLE, width=30, height=8)
concepts = ["Phishing", "Malware", "Firewall", "Chiffrement", "VPN"]

# Ajout des concepts à la Listbox
for concept in concepts:
    listbox.insert(tk.END, concept)

listbox.pack(pady=10)

# Bouton pour afficher la sélection
btn_afficher = tk.Button(fenetre, text="Afficher", command=afficher_selection)
btn_afficher.pack(pady=5)

# Lancement de l'application
fenetre.mainloop()
