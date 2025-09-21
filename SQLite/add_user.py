import sqlite3
import bcrypt
import os

sqlite_path = "./data/bdd_connexion.sqlite"

os.makedirs("./data", exist_ok=True)  # vérifier que data existe

def add_user(nom_utilisateur, identifiant, mot_de_passe, role_id):
    """Ajoute un utilisateur après vérification"""

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

      # Vérifier si l'identifiant existe déjà pour ce rôle
    cur.execute(
        "SELECT mot_de_passe FROM utilisateurs WHERE identifiant = ? AND role_id = ?",
        (identifiant, role_id)
    )
    result = cur.fetchone()

    if result:
        # Utilisateur existe déjà pour ce rôle → vérifier le mot de passe
        stored_hashed_password = result[0]

        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), stored_hashed_password):
            print("L'utilisateur existe déjà")
        else:
            print("Mot de passe incorrect.")
        conn.close()
        return

    # Sinon (identifiant pas encore utilisé pour ce rôle) → on ajoute
    hashed_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
    cur.execute(
        "INSERT INTO utilisateurs (nom_utilisateur, identifiant, mot_de_passe, role_id) VALUES (?, ?, ?, ?)",
        (nom_utilisateur, identifiant, hashed_password, role_id)
    )
    conn.commit()
    conn.close()
    print(f"L'tilisateur {nom_utilisateur} ajouté avec succès (identifiant '{identifiant}', rôle {role_id}).")

if __name__ == "__main__":

    nom = input("Nom complet : ")
    identifiant = input("Identifiant : ")
    mdp = input("Mot de passe : ")
    role = int(input("Role ID (1=enseignant, 2=etudiant, 3=administrateur) : "))

    add_user(nom, identifiant, mdp, role)