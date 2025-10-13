from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# URL et nom de la base
MONGO_URI = "mongodb://isen:isen@localhost:27017/"
DB_NAME = "quiz_db"

# Connexion globale
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Connexion MongoDB réussie.")
except ConnectionFailure:
    print("Impossible de se connecter à MongoDB.")
    db = None

# Collections principales
questions_collection = db["questions"]
questionnaires_collection = db["questionnaires"]
subjects_collection = db["subjects"]
test_types_collection = db["test_types"]

# Optionnel : fonction pour tester la connexion
def test_connection():
    if db is not None:
        print("Collections disponibles :", db.list_collection_names())
    else:
        print("Connexion MongoDB non initialisée.")

if __name__ == "__main__":
    test_connection()
