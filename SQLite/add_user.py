import sqlite3
import bcrypt
import os


sqlite_path = "./data/bdd_connexion.sqlite"

os.makedirs("./data", exist_ok=True) #vérifier que data existe

def add_user(nom_utilisateur, identifiant, mot_de_passe, role_id):
    """Ajoute un utilisateur avec mot de passe haché"""

    hashed_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO utilisateurs (nom_utilisateur, identifiant, mot_de_passe, role_id) VALUES (?, ?, ?, ?)",
        (nom_utilisateur, identifiant, hashed_password, role_id)
        )
    conn.commit()
    conn.close()
    print(f"Utilisateur {nom_utilisateur} ajouté avec succès.")

if __name__ == "__main__":
    # Demande à l’utilisateur les infos
    nom = input("Nom complet : ")
    identifiant = input("Identifiant : ")
    mdp = input("Mot de passe : ")
    role = int(input("Role ID (1=enseignant, 2=etudiant, 3=administrateur) : "))

    add_user(nom, identifiant, mdp, role)    