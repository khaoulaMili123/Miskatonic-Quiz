import sqlite3
import bcrypt
import os

sqlite_path = "./data/bdd_connexion.sqlite"

os.makedirs("./data", exist_ok=True)  # vérifier que data existe

def add_users(nom_utilisateur, identifiant, mot_de_passe, role_id):
    """
    Vérifie si l'utilisateur existe :
      - Si existe + mdp correct → connexion
      - Si existe + mdp incorrect → demander changement
      - Si n'existe pas → proposer création
    """
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    cur.execute("SELECT mot_de_passe FROM utilisateurs WHERE identifiant=? AND role_id=?", 
                (identifiant, role_id))
    result = cur.fetchone()

    if result:
        stored_hashed_password = result[0]
        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), stored_hashed_password):
            conn.close()
            return True, "Connexion réussie."
        else:
            conn.close()
            return False, "Mot de passe incorrect, veuillez le changer."
    else:
        conn.close()
        return False, "Identifiant inconnu, veuillez créer un compte."

if __name__ == "__main__":

    nom = input("Nom complet : ")
    identifiant = input("Identifiant : ")
    mdp = input("Mot de passe : ")
    role = int(input("Role ID (1=enseignant, 2=etudiant, 3=administrateur) : "))

    add_users(nom, identifiant, mdp, role)