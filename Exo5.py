import tkinter as tk

def verifier_mode():
    if var_mode.get():
        label_resultat.config(text="Mode sécurisé activé", fg="green")
    else:
        label_resultat.config(text="Mode standard activé", fg="blue")

# Fenêtre principale
fenetre = tk.Tk()
fenetre.title("Mode sécurisé")
fenetre.geometry("300x180")

# Variable pour stocker l'état de la case à cocher
var_mode = tk.BooleanVar()

# Checkbutton
check = tk.Checkbutton(fenetre, text="Activer le mode sécurisé", variable=var_mode)
check.pack(pady=15)

# Bouton Vérifier
bouton_verifier = tk.Button(fenetre, text="Vérifier", command=verifier_mode)
bouton_verifier.pack(pady=10)

# Label pour afficher le résultat
label_resultat = tk.Label(fenetre, text="", font=("Arial", 11))
label_resultat.pack(pady=10)

# Lancement de l'application
fenetre.mainloop()
