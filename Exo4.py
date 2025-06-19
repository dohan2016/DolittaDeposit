import tkinter as tk

def calculer(operation):
    try:
        # Récupérer les valeurs saisies
        val1 = float(entree1.get())
        val2 = float(entree2.get())

        # Réaliser l'opération choisie
        if operation == "+":
            resultat = val1 + val2
        elif operation == "-":
            resultat = val1 - val2
        elif operation == "*":
            resultat = val1 * val2
        elif operation == "/":
            if val2 == 0:
                label_resultat.config(text="Division par zéro interdite", fg="red")
                return
            resultat = val1 / val2

        label_resultat.config(text=f"Résultat : {resultat}", fg="green")

    except ValueError:
        label_resultat.config(text="Erreur : entrez des nombres valides.", fg="red")

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Mini Calculatrice")
fenetre.geometry("350x250")

# Champs de saisie
tk.Label(fenetre, text="Nombre 1 :").pack()
entree1 = tk.Entry(fenetre)
entree1.pack(pady=5)

tk.Label(fenetre, text="Nombre 2 :").pack()
entree2 = tk.Entry(fenetre)
entree2.pack(pady=5)

# Boutons d'opérations
frame_boutons = tk.Frame(fenetre)
frame_boutons.pack(pady=10)

tk.Button(frame_boutons, text="+", width=5, command=lambda: calculer("+")).grid(row=0, column=0, padx=5)
tk.Button(frame_boutons, text="-", width=5, command=lambda: calculer("-")).grid(row=0, column=1, padx=5)
tk.Button(frame_boutons, text="*", width=5, command=lambda: calculer("*")).grid(row=0, column=2, padx=5)
tk.Button(frame_boutons, text="/", width=5, command=lambda: calculer("/")).grid(row=0, column=3, padx=5)

# Label pour afficher le résultat
label_resultat = tk.Label(fenetre, text="", font=("Arial", 12))
label_resultat.pack(pady=15)

# Lancement de l'application
fenetre.mainloop()
