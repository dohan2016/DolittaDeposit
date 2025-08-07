import random
import string

def generer_mot_de_passe(longueur=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choice(caracteres) for _ in range(longueur))
