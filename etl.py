import pandas as pd
import json

def etl_quiz():
    df= pd.read_csv("./data/questions.csv")
    #df = df.iloc[:-8]
    print (df)
    
    #colonnes contenant les réponses
    response_cols = [col for col in df.columns if col.lower().startswith('response')]
    #print (response_cols)

    #tous les réponses pour chaque ligne
    df['all_responses'] = df[response_cols].apply(
        lambda x: [resp for resp in x if pd.notna(resp)], axis=1)
    #Supprimer les deux-points dans les questions
    df['question'] = df['question'].str.replace(":", "", regex=False)
    
    # Créer pour chaque ligne la ou les bonnes réponses (texte)
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
    # Supprimer les lignes invalides :
    df = df[df['question'].notna()]                          # question non nulle
    df = df[df['question'].str.strip() != ""]                # question non vide
    df = df[df['all_responses'].map(len) > 0]                # au moins une réponse
    df = df[df['correct_responses'].map(len) > 0]            # au moins une bonne réponse

    # Nettoyer encore une fois les listes (au cas où) :
    df['all_responses'] = df['all_responses'].apply(lambda lst: [r for r in lst if str(r).strip() != ""])
    df['correct_responses'] = df['correct_responses'].apply(lambda lst: [r for r in lst if str(r).strip() != ""])
    print (df)
    #Regrouper par question pour fusionner les réponses et bonnes réponses
    grouped = (df.groupby('question')
               .agg({
                   'subject': 'first',
                   'all_responses': lambda x: list({resp for sublist in x for resp in sublist}),
                   'correct_responses': lambda x: list({resp for sublist in x for resp in sublist})
               })
               .reset_index())
    #print (df)
    #Convertir en dictionnaires et exporter en JSON
    output_json= "./data/questions.json"
    records = grouped.to_dict(orient='records')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Fichier JSON créé : {output_json}")

if __name__ == "__main__":
    etl_quiz()