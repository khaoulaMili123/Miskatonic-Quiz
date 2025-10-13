from pydantic import BaseModel

class UserCreate(BaseModel):
    nom_utilisateur: str
    identifiant: str
    mot_de_passe: str
    role_id: int = 1 # Par défaut, enseignant

class User(BaseModel):
    id: int
    nom_utilisateur: str
    identifiant: str
    role_id: int

    class Config:
        from_attributes = True
