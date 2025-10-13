from fastapi import APIRouter, HTTPException, status, Depends, Query
from pymongo import MongoClient
from typing import List
from app.models.questions_model import QuestionCreate, Question
import math

router = APIRouter()

# Configuration de la connexion MongoDB
CLIENT = MongoClient("mongodb://isen:isen@localhost:27017/?authSource=admin")
DB = CLIENT['quiz_db']
QUESTIONS_COLLECTION = DB['questions']

@router.get("/subjects", response_model=List[str])
def get_subjects():
    """Récupère la liste unique de tous les sujets de questions."""
    try:
        return QUESTIONS_COLLECTION.distinct("subject")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/uses", response_model=List[str])
def get_uses():
    """Récupère la liste unique de tous les types de test (use)."""
    try:
        return QUESTIONS_COLLECTION.distinct("use")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Question])
def get_questions(
    subjects: List[str] = Query(None),
    uses: List[str] = Query(None),
    quantity: int = 20
):
    """
    Récupère une liste de questions filtrées et la transforme pour correspondre au modèle.
    """
    try:
        match_filter = {}
        if subjects:
            match_filter['subject'] = {'$in': subjects}
        if uses:
            match_filter['use'] = {'$in': uses}

        pipeline = [
            {'$match': match_filter},
            {'$sample': {'size': quantity}}
        ]
        
        questions_from_db = list(QUESTIONS_COLLECTION.aggregate(pipeline))
        
        # --- Transformation des données ---
        transformed_questions = []
        for q in questions_from_db:
            # Créer le champ 'id' à partir de '_id' et supprimer l'ancien
            q['id'] = str(q.pop('_id'))

            # Créer le dictionnaire de réponses
            responses_dict = {}
            for key in ['responseA', 'responseB', 'responseC', 'responseD']:
                if key in q and isinstance(q[key], str):
                    responses_dict[key[-1]] = q.pop(key) # .pop pour nettoyer
            q['responses'] = responses_dict

            # Nettoyer la remarque
            if 'remark' not in q or not isinstance(q['remark'], str):
                q['remark'] = ""

            # Assurer que tous les champs du modèle sont présents
            for field in QuestionCreate.model_fields:
                if field not in q:
                    q[field] = "" # ou une autre valeur par défaut appropriée
            
            transformed_questions.append(q)

        return transformed_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_question(question: QuestionCreate):
    """
    Ajoute une nouvelle question à la base de données.
    """
    try:
        question_dict = question.model_dump()
        result = QUESTIONS_COLLECTION.insert_one(question_dict)
        
        return {
            "message": "Question ajoutée avec succès !",
            "question_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de l'ajout de la question: {e}"
        )
