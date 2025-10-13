from pydantic import BaseModel, Field
from typing import Dict
from bson import ObjectId # Importé au bon endroit

class QuestionCreate(BaseModel):
    subject: str
    use: str # Type de test
    question: str
    responses: Dict[str, str] # ex: {"A": "Paris", "B": "Londres"}
    correct: str # ex: "A" ou "A,B"
    remark: str | None = None

class Question(QuestionCreate):
    id: str = Field(..., alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
        # Indique à Pydantic comment convertir un ObjectId en chaîne de caractères
        json_encoders = {
            ObjectId: str
        }