from pydantic import BaseModel
from typing import List

class QuizCreate(BaseModel):
    title: str
    question_ids: List[str]
