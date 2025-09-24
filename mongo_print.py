from pymongo import MongoClient
from pprint import pprint

client = MongoClient("mongodb://localhost:27017/")
db = client.miskatonic_db
questions = db.questions

# Afficher les 3 premières questions
for q in questions.find().limit(3):
    pprint(q)