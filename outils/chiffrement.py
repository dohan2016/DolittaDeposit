from Crypto.Cipher import AES
import base64
import hashlib

def chiffrer_cesar(texte, cle):
    try:
        cle = int(cle)
    except ValueError:
        return "Clé invalide (doit être un entier)"
    resultat = ""
    for c in texte:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            resultat += chr((ord(c) - base + cle) % 26 + base)
        else:
            resultat += c
    return resultat

def dechiffrer_cesar(texte, cle):
    try:
        cle = int(cle)
    except ValueError:
        return "Clé invalide (doit être un entier)"
    return chiffrer_cesar(texte, -cle)

def _aes_get_cipher(key):
    key_bytes = hashlib.sha256(key.encode()).digest()
    return AES.new(key_bytes, AES.MODE_ECB)

def chiffrer_aes(texte, cle):
    cipher = _aes_get_cipher(cle)
    pad = 16 - len(texte) % 16
    texte_padded = texte + chr(pad) * pad
    encrypted = cipher.encrypt(texte_padded.encode())
    return base64.b64encode(encrypted).decode()

def dechiffrer_aes(texte, cle):
    cipher = _aes_get_cipher(cle)
    try:
        decoded = base64.b64decode(texte)
        decrypted = cipher.decrypt(decoded).decode()
        pad = ord(decrypted[-1])
        return decrypted[:-pad]
    except Exception:
        return "Erreur : clé incorrecte ou texte corrompu"
