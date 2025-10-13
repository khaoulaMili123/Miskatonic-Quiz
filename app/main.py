from fastapi import FastAPI
from app.routers import auth, questions, quizzes

app = FastAPI(
    title="Miskatonic Quiz API",
    description="API pour la gestion des quiz, des questions et des utilisateurs.",
    version="1.0.0"
)

# Inclure les routeurs
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API du Miskatonic Quiz"}
