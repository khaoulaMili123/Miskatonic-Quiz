import sys
import os
from fastapi import APIRouter, HTTPException, status

# Ajoute le chemin racine au sys.path pour trouver le module SQLite
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.user_model import UserCreate
from SQLite.add_user import register_user as register_user_in_db

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """
    Inscrit un nouvel utilisateur dans la base de données SQLite.
    """
    success, message = register_user_in_db(
        nom_utilisateur=user.nom_utilisateur,
        identifiant=user.identifiant,
        mot_de_passe=user.mot_de_passe,
        role_id=user.role_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict est approprié si l'utilisateur existe déjà
            detail=message
        )
    
    return {"message": message}
