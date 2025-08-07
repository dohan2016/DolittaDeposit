import hashlib

def hasher_texte(texte, algorithme="sha256"):
    h = hashlib.new(algorithme)
    h.update(texte.encode('utf-8'))
    return h.hexdigest()
