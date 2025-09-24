from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'vraiment_secret'

# Stock de questions par catégorie
stock_questions = {
    'Test de validation': 29,
    'Test de positionnement': 21,
    'Total Bootcamp': 15
}

nombres_possibles = [5, 10, 15, 30, 50]

@app.route('/')
def index():
    return redirect(url_for('selection'))

@app.route('/selection', methods=['GET', 'POST'])
def selection():
    if request.method == 'POST':
        categories = request.form.getlist('categorie')  # plusieurs catégories possibles
        nombre = request.form.get('nombre')             # un seul nombre choisi

        if not categories or not nombre:
            flash("Veuillez choisir au moins une catégorie et un nombre de questions.")
            return redirect(url_for('selection'))

        return f"<h2>Quiz: {', '.join(categories)} avec {nombre} questions</h2>"

    # Si GET, on affiche simplement le formulaire
    return render_template('selection.html', categories=list(stock_questions.keys()), nombres=nombres_possibles)


if __name__ == '__main__':
    app.run(debug=True)
