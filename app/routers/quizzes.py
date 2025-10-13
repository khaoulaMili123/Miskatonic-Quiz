from fastapi import APIRouter, HTTPException, status
from pymongo import MongoClient
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List

from app.models.quiz_model import QuizCreate

router = APIRouter()

# Connexion MongoDB
CLIENT = MongoClient("mongodb://isen:isen@localhost:27017/?authSource=admin")
DB = CLIENT['quiz_db']
QUESTIONS_COLLECTION = DB['questions']
QUESTIONNAIRES_COLLECTION = DB['questionnaires']


@router.get("/")
def get_all_quizzes():
    """Récupère la liste de tous les questionnaires (titre et ID)."""
    try:
        quizzes = list(QUESTIONNAIRES_COLLECTION.find({}, {"title": 1}))
        for quiz in quizzes:
            quiz["_id"] = str(quiz["_id"])
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quiz_id}")
def get_quiz_by_id(quiz_id: str):
    """Récupère un questionnaire complet par son ID."""
    try:
        quiz = QUESTIONNAIRES_COLLECTION.find_one({"_id": ObjectId(quiz_id)})
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz non trouvé.")
        
        quiz["_id"] = str(quiz["_id"])
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_quiz(quiz_data: QuizCreate):
    """
    Crée un nouveau quiz (questionnaire) à partir d'un titre et d'une liste d'IDs de questions.
    Récupère les détails de chaque question et les intègre dans le document du quiz.
    """
    try:
        # Convertir les IDs de string à ObjectId
        object_ids = [ObjectId(qid) for qid in quiz_data.question_ids]

        # Récupérer toutes les questions correspondantes en une seule requête
        questions_cursor = QUESTIONS_COLLECTION.find({"_id": {"$in": object_ids}})
        questions_list = list(questions_cursor)

        # Vérifier si toutes les questions ont été trouvées
        if len(questions_list) != len(quiz_data.question_ids):
            raise HTTPException(status_code=404, detail="Une ou plusieurs questions n'ont pas été trouvées.")

        # Convertir les ObjectId en string pour le stockage final
        for q in questions_list:
            q['_id'] = str(q['_id'])

        # Créer le document final du quiz
        new_quiz_doc = {
            "title": quiz_data.title,
            "questions": questions_list
        }

        result = QUESTIONNAIRES_COLLECTION.insert_one(new_quiz_doc)

        return {
            "message": "Quiz créé avec succès !",
            "quiz_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
