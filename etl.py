import pandas as pd
 
 
questions_path = "./data/questions.csv"
 
 
def run_etl():
    df = pd.read_csv(questions_path)
    print(f"✅ Fichier chargé : {questions_path} ({len(df)} lignes)")
 
    print(df.head())    # Affiche les 5 premières lignes
    print(len(df))      # Nombre de lignes
    print(df.columns)   # Colonnes du dataframe
 
# Appel fonction
if __name__ == "__main__":
    run_etl()