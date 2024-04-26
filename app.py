from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_game.db"
app.config["SECRET_KEY"] = "secret_key"
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    score = db.Column(db.Integer, default=0)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    choices = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    correct_choice = db.Column(db.Integer, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/leaderboard")
def leaderboard():
    players = Player.query.order_by(Player.score.desc()).all()
    return render_template("leaderboard.html", players=players)

@app.route("/start_game", methods=["GET", "POST"])
def start_game():
    if request.method == "POST":
        name = request.form.get("name")
        existing_player = Player.query.filter_by(name=name).first()
        if existing_player:
            return "Player already exists. Please choose another name."
        else:
            session["player_name"] = name
            return redirect("/select_difficulty")
    return render_template("start_game.html")

@app.route("/add_question_form")
def add_question_form():
    return render_template("add_question_form.html")

@app.route("/add_question", methods=["POST"])
def add_question():
    text = request.form.get("text")
    choices = [request.form.get(f"choice{i}") for i in range(1, 5)]
    difficulty = request.form.get("difficulty")
    correct_choice = int(request.form.get("correct_choice"))

    new_question = Question(text=text, choices=",".join(choices), difficulty=difficulty, correct_choice=correct_choice)
    db.session.add(new_question)
    db.session.commit()

    return render_template("add_question_success.html")

@app.route("/questions")
def list_questions():
    questions = Question.query.all() 
    return render_template("question_list.html", questions=questions)

@app.route('/delete/<int:id>')
def delete(id):
 delete_task = Question.query.get(id)
 db.session.delete(delete_task)
 db.session.commit()
 return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
 update_task = Question.query.get(id)
 if request.method == 'GET':
  return render_template('question_update.html',question=update_task)
 if request.method == "POST":
        text = request.form.get("text")
        choices = [request.form.get(f"choice{i}") for i in range(1, 5)]
        difficulty = request.form.get("difficulty")
        correct_choice = int(request.form.get("correct_choice"))

        update_task.text = text
        update_task.choices = ",".join(choices)
        update_task.difficulty = difficulty
        update_task.correct_choice = correct_choice

        db.session.commit()
        return redirect("/questions")

# @app.route("/select_difficulty")
# def select_difficulty():
#     return render_template("select_difficulty.html")

# @app.route("/select_difficulty_decision", methods=["GET", "POST"])
# def select_difficulty_decision():
#     if request.method == "POST":
#         session["difficulty"] = request.form.get("difficulty")
#         return redirect("/play_game")
#     return render_template("select_difficulty.html")

# @app.route("/play_game", methods=["GET", "POST"])
# def play_game():
#     difficulty = session.get("difficulty")
#     question = Question.query.filter_by(difficulty=difficulty).order_by(func.random()).first()
#     if request.method == "POST":
#         selected_choice = int(request.form.get("choice"))
#         if selected_choice == question.correct_choice:
#             player = Player.query.filter_by(name=session["player_name"]).first()
#             player.score += 10
#             db.session.commit()
#         return redirect("/play_game")
#     return render_template("play_game.html", question=question)

if __name__ == "__main__":
    app.run(debug=True)
