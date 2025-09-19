import sqlite3
import hashlib

DB_NAME = "users.db"

def create_tables():
    """Créer les tables Roles et Utilisateurs si elles n'existent pas."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        # Table Roles
        c.execute("""
            CREATE TABLE IF NOT EXISTS Roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_role TEXT NOT NULL UNIQUE
            );
        """)
        # Table Utilisateurs
        c.execute("""
            CREATE TABLE IF NOT EXISTS Utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT NOT NULL,
                identifiant TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                FOREIGN KEY (role_id) REFERENCES Roles(id)
            );
        """)
        # Insertion des rôles par défaut
        roles = [(1, "Administrateur"), (2, "Enseignant"), (3, "Etudiant")]
        c.executemany(
            "INSERT OR IGNORE INTO Roles (id, nom_role) VALUES (?, ?);", roles
        )
        conn.commit()

create_tables()
