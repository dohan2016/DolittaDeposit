# 🛡️ SDH Security – Gestionnaire d'accès réseau

**SDH_Security** est une application développée en Python avec PyQt5 pour gérer des utilisateurs dans un réseau local, avec des outils intégrés de cybersécurité :

- Gestion des utilisateurs (ajout, suppression, activation, etc.)
- Génération de mot de passe sécurisé
- Hashage de texte (SHA256, MD5…)
- Chiffrement / Déchiffrement (César, AES)

---

## 📸 Aperçu

![interface](assets/screenshot_main.png)

---

## 🧰 Fonctionnalités principales

### ✅ Gestion d'utilisateurs
- Ajouter un utilisateur (nom, email)
- Générer automatiquement un mot de passe
- Activer / désactiver un utilisateur
- Supprimer un utilisateur
- Sauvegarder / charger la liste des utilisateurs (`JSON`)

### 🔐 Outils de cybersécurité
- **Hashage de texte** (SHA-256, MD5)
- **Générateur de mot de passe** (longueur personnalisable)
- **Chiffrement / Déchiffrement** :
  - César
  - AES (mode ECB, avec clé)

---

## 🏗️ Structure du projet


