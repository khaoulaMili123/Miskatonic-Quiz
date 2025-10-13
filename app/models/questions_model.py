from pydantic import BaseModel, Field
from typing import Dict

class QuestionCreate(BaseModel):
    subject: str
    use: str
    question: str
    responses: Dict[str, str]
    correct: str
    remark: str

class Question(QuestionCreate):
    id: str