from pymongo import MongoClient
import pandas as pd

def etl_quiz():
    df = pd.read_csv("./data/questions.csv")
    print("CSV chargé :", df.shape, "lignes")

    response_cols = [col for col in df.columns if col.lower().startswith('response')]
    df['all_responses'] = df[response_cols].apply(
        lambda x: [resp for resp in x if pd.notna(resp)], axis=1
    )
    df['question'] = df['question'].str.replace(":", "", regex=False)

    def get_correct_responses(row):
        correct_letters = str(row['correct']).split(',')
        correct_answers = []
        for letter in correct_letters:
            letter = letter.strip().upper()
            colname = f"response{letter}"
            if colname in row and pd.notna(row[colname]):
                correct_answers.append(row[colname])
        return correct_answers

    df['correct_responses'] = df.apply(get_correct_responses, axis=1)

    # Filtrer lignes invalides
    df = df[df['question'].notna()]
    df = df[df['question'].str.strip() != ""]
    df = df[df['all_responses'].map(len) > 0]
    df = df[df['correct_responses'].map(len) > 0]

    df['all_responses'] = df['all_responses'].apply(lambda lst: [r for r in lst if str(r).strip() != ""])
    df['correct_responses'] = df['correct_responses'].apply(lambda lst: [r for r in lst if str(r).strip() != ""])

    # Connexion MongoDB
    client = MongoClient("mongodb://isen:isen@localhost:27017/?authSource=admin")
    db = client['quiz_db']

    # --- Collection questions ---
    collection_q = db['questions']
    collection_q.delete_many({})
    records = df.to_dict(orient='records')
    collection_q.insert_many(records)
    print(f"{len(records)} questions insérées dans la collection 'questions'")

    # --- Collection subjects ---
    collection_s = db['subjects']
    collection_s.delete_many({})
    subjects_grouped = df.groupby('subject', group_keys=False).apply(
        lambda x: x[['question', 'use', 'all_responses', 'correct_responses']].to_dict(orient='records')
    ).reset_index()

    subjects_records = []
    for _, row in subjects_grouped.iterrows():
        subjects_records.append({
            "subject": row['subject'],
            "questions": row[0]
        })
    collection_s.insert_many(subjects_records)
    print(f"{len(subjects_records)} sujets insérés dans la collection 'subjects'")

    # --- Collection test_types ---
    collection_test = db['test_types']
    collection_test.delete_many({})

    test_grouped = df.groupby('use', group_keys=False).apply(
        lambda x: x[['subject', 'question', 'all_responses', 'correct_responses']].to_dict(orient='records')
    ).reset_index()

    test_records = []
    for _, row in test_grouped.iterrows():
        test_records.append({
            "test_type": row['use'],
            "questions": row[0]
        })
    collection_test.insert_many(test_records)
    print(f"{len(test_records)} types de tests insérés dans la collection 'test_types'")

    # --- Collection questionnaires (vide) ---
    collection_questionnaires = db['questionnaires']
    collection_questionnaires.delete_many({})
    print("Collection 'questionnaires' créée vide")

if __name__ == "__main__":
    etl_quiz()
