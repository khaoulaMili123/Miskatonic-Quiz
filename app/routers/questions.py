from fastapi import APIRouter, HTTPException, status, Depends, Query
from pymongo import MongoClient
from typing import List
from app.models.questions_model import QuestionCreate

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

@router.get("/", response_model=List[dict])
def get_questions(
    subjects: List[str] = Query(None),
    uses: List[str] = Query(None),
    quantity: int = 20
):
    print(f"Filtres reçus - Sujets: {subjects}, Types: {uses}") # Ligne de débogage
    """
    Récupère une liste de questions filtrées par sujet(s) et/ou type(s) de test,
    et échantillonnées à une certaine quantité.
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
        
        questions = list(QUESTIONS_COLLECTION.aggregate(pipeline))
        # Convertir ObjectId en str pour la sérialisation JSON
        for q in questions:
            q['_id'] = str(q['_id'])
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
# ... (le reste de la fonction create_question)
def create_question(question: QuestionCreate):
    """
    Ajoute une nouvelle question à la base de données.
    
    (Pour l'instant, cette route n'est pas protégée, mais elle le sera)
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
