import sqlite3, os

os.makedirs("./data", exist_ok=True)  # créer le dossier si besoin

sqlite_path = "./data/bdd_connexion.sqlite"
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

cur.executescript("""
    DROP TABLE IF EXISTS utilisateurs;
    DROP TABLE IF EXISTS roles;

    CREATE TABLE roles(
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL
    );
    
    CREATE TABLE utilisateurs(
        utilisateur_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_utilisateur TEXT NOT NULL,
        identifiant TEXT NOT NULL,
        mot_de_passe TEXT NOT NULL,
        role_id INTEGER,
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
    );
""")

roles = [
    ("enseignant",),
    ("etudiant",),
    ("administrateur",)
]
cur.executemany("INSERT INTO roles (role) VALUES (?);", roles)

conn.commit()
conn.close()

print(f"Base créée et roles insérés dans {sqlite_path}")

