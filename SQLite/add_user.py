import sqlite3
import bcrypt
import os

sqlite_path = "./data/bdd_connexion.sqlite"
os.makedirs("./data", exist_ok=True)

# ---- LOGIN ----
def add_users(nom_utilisateur, identifiant, mot_de_passe, role_id):
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    cur.execute("SELECT mot_de_passe FROM utilisateurs WHERE identifiant=? AND role_id=?", 
                (identifiant, role_id))
    result = cur.fetchone()

    if result:
        stored_hashed_password = result[0]
        if isinstance(stored_hashed_password, str):
            stored_hashed_password = stored_hashed_password.encode('utf-8')
        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), stored_hashed_password):
            conn.close()
            return True, "Connexion réussie."
        else:
            conn.close()
            return False, "Mot de passe incorrect, veuillez le changer."
    else:
        conn.close()
        return False, "Identifiant inconnu, veuillez créer un compte."

# ---- CREATION UTILISATEUR ----
def register_user(nom_utilisateur, identifiant, mot_de_passe, role_id):
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    # Vérifie si identifiant déjà utilisé
    cur.execute("SELECT * FROM utilisateurs WHERE identifiant=?", (identifiant,))
    result = cur.fetchone()

    if result:
        conn.close()
        return False, "Identifiant déjà utilisé, changez votre mot de passe"

    hashed_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
    cur.execute(
        "INSERT INTO utilisateurs (nom_utilisateur, identifiant, mot_de_passe, role_id) VALUES (?, ?, ?, ?)",
        (nom_utilisateur, identifiant, hashed_password, role_id)
    )
    conn.commit()
    conn.close()
    return True, "Vous êtes bien inscrit !"
