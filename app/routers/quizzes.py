from fastapi import APIRouter, HTTPException, status
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List
import math

from app.models.quiz_model import QuizCreate

router = APIRouter()

# Connexion MongoDB
CLIENT = MongoClient("mongodb://isen:isen@localhost:27017/?authSource=admin")
DB = CLIENT['quiz_db']
QUESTIONS_COLLECTION = DB['questions']
QUESTIONNAIRES_COLLECTION = DB['questionnaires']


def clean_nans(obj):
    """Récursivement, remplace les valeurs NaN par des chaînes vides."""
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return ""
    return obj


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
    """Récupère un questionnaire complet et le formate pour l'affichage."""
    try:
        quiz = QUESTIONNAIRES_COLLECTION.find_one({"_id": ObjectId(quiz_id)})
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz non trouvé.")
        
        # Nettoyer les NaNs potentiels à la lecture
        quiz = clean_nans(quiz)

        # Transformer les questions imbriquées
        if 'questions' in quiz and isinstance(quiz['questions'], list):
            formatted_questions = []
            for q in quiz['questions']:
                responses_dict = {}
                for key in ['responseA', 'responseB', 'responseC', 'responseD']:
                    if key in q and q[key]:
                        responses_dict[key[-1]] = q.pop(key)
                q['responses'] = responses_dict
                formatted_questions.append(q)
            quiz['questions'] = formatted_questions

        quiz["_id"] = str(quiz["_id"])
        return quiz

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_quiz(quiz_data: QuizCreate):
    """
    Crée un nouveau quiz en nettoyant les données des questions avant de les intégrer.
    """
    try:
        # Filtrer les chaînes vides qui pourraient être envoyées par le formulaire
        valid_question_ids = [qid for qid in quiz_data.question_ids if qid]
        if not valid_question_ids:
            raise HTTPException(status_code=400, detail="La liste des IDs de questions est vide.")

        object_ids = [ObjectId(qid) for qid in valid_question_ids]

        questions_cursor = QUESTIONS_COLLECTION.find({"_id": {"$in": object_ids}})
        questions_list = list(questions_cursor)

        if len(questions_list) != len(valid_question_ids):
            raise HTTPException(status_code=404, detail="Une ou plusieurs questions n'ont pas été trouvées.")

        # Nettoyer les NaNs de chaque question avant de les intégrer
        cleaned_questions = [clean_nans(q) for q in questions_list]

        for q in cleaned_questions:
            q['_id'] = str(q['_id'])

        new_quiz_doc = {
            "title": quiz_data.title,
            "questions": cleaned_questions
        }

        result = QUESTIONNAIRES_COLLECTION.insert_one(new_quiz_doc)

        return {
            "message": "Quiz créé avec succès !",
            "quiz_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{quiz_id}", status_code=status.HTTP_200_OK)
def delete_quiz(quiz_id: str):
    """Supprime un quiz par son ID."""
    try:
        result = QUESTIONNAIRES_COLLECTION.delete_one({"_id": ObjectId(quiz_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Quiz non trouvé.")
        return {"message": "Quiz supprimé avec succès."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
