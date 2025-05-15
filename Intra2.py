# Nom de l'algorithme : Maximum3Nombres
# Rôle : Cet algorithme permet de lire trois nombres donnés par l'utilisateur et de déterminer lequel est le plus grand parmi eux.

nombre1 = float(input("Entrez le premier nombre : "))
nombre2 = float(input("Entrez le deuxième nombre : "))
nombre3 = float(input("Entrez le troisième nombre : "))

if nombre1 > nombre2 and nombre1 > nombre3:
    max_val = nombre1
elif nombre2 > nombre1 and nombre2 > nombre3:
    max_val = nombre2
else:
    max_val = nombre3

print("Le maximum est :", max_val)
