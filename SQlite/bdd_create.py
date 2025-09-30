import sqlite3
import hashlib

DB_NAME = "users.db"

def create_table_and_insert():
    """Créer la table Utilisateurs si elle n'existe pas."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Créer la table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT NOT NULL,
                identifiant TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                secret_code TEXT NOT NULL
            );
        """)

        # Insérer des données de base
        c.executemany("""
            INSERT OR IGNORE INTO Utilisateurs (nom_utilisateur, identifiant, mot_de_passe, secret_code)
            VALUES (?, ?, ?, ?)
        """, [
            ('Directrice', 'directrice', 'ef92b778bafe771e89245b89ecbcdf2347f66c2edab2f9a6c80a48b8d56f3e69', 'code123'),
            ('M. Dupont', 'mdupont', '9c75e93006bdb7c60a87f5bcb71dbca20e9620e2321245b3af5f6ed72a7f4c68', 'secret456'),
            ('Mme Martin', 'mmartin', 'b9b37b2b90a3e89616aa11182c1f6c77f2e6b6813bbd7de588a9f9a68b0b6bc3', 'secret789')
        ])

        conn.commit()

create_table_and_insert()