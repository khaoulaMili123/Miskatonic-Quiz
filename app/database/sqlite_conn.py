import sqlite3
import os
from contextlib import contextmanager

# Chemin vers la base SQLite existante
DB_PATH = os.path.join("./data/bdd_connexion.sqlite")

# Assure que le dossier existe
os.makedirs("./data", exist_ok=True)

@contextmanager
def get_db_connection():
    """
    Fournit une connexion SQLite réutilisable.
    La connexion se ferme automatiquement après usage.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
