from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import func
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

error_message=""
@app.route("/")
def index():
    global error_message
    error_message=""
    return render_template("index.html")

@app.route("/leaderboard")
def leaderboard():
    players = Player.query.order_by(Player.score.desc()).all()
    return render_template("leaderboard.html", players=players)

id = 0
"""
@app.route("/start_game", methods=["GET", "POST"])
def start_game():
    if request.method == "POST":
        global id
        id += 1
        name = request.form.get("name")
        existing_player = Player.query.filter_by(name=name).first()
        if existing_player:
            return "Player already exists. Please choose another name."
        else:
            new_player = Player(id=id, name=name, score=0)
            db.session.add(new_player)
            db.session.commit()
            session["player_name"] = name
            return redirect("/select_difficulty")
    return render_template("start_game.html")
    """

@app.route("/start_game", methods=["GET", "POST"])
def start_game():
    if request.method == "POST":
        name = request.form.get('name')

        existing_player = Player.query.filter_by(name=name).first()
        if existing_player:
            global error_message
            error_message = 'この名前のプレイヤーは既に登録されています。別の名前を選んでください。'
            #session['error_message'] = error_message
            #error_message = session.pop('error_message', None)
            return redirect("/start_game")

        # Register new player
        new_player = Player(name=name)
        db.session.add(new_player)
        session["player_name"] = name
        db.session.commit()
        return redirect("/select_difficulty")
    return render_template("start_game.html", error_message=error_message)

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

num = 0
@app.route("/select_difficulty", methods=["GET", "POST"])
def select_difficulty_decision():
    if request.method == "POST":
        session["difficulty"] = request.form
        global num
        num = 0
        return redirect("/play_game")
    return render_template("select_difficulty.html")


@app.route("/play_game", methods=["GET", "POST"])
def play_game():
    each_level_questions = []
    difficulty = list(session.get("difficulty").values())
    questions = Question.query.all()
    for question in questions:
        if question.difficulty == difficulty[0]:
            each_level_questions.append(question)
    choices_list = []
    for question in each_level_questions:
        choices_list.append(question.choices.split(","))
    print(each_level_questions)
    print(choices_list)
    #question = Question.query.filter_by(Question.query.difficulty==difficulty[0])

    if request.method == "POST":
        global num
        num += 1
        selected_choice = []
        tf="False"
        #selected_choice = int(request.form.values()[0])
        selected_choice.append(request.form.get("1"))
        selected_choice.append(request.form.get("2"))
        selected_choice.append(request.form.get("3"))
        selected_choice.append(request.form.get("4"))
        print(selected_choice)
        print(question.correct_choice)
        print(selected_choice[question.correct_choice-1])
        print(selected_choice[question.correct_choice-1] == str(question.correct_choice))
        if selected_choice[question.correct_choice-1] == str(question.correct_choice):
            #player = Player.query.filter_by(name=session["player_name"]).first()
            players = Player.query.all()
            for each_player in players:
                if each_player.name == session["player_name"]:
                    player = each_player
            if difficulty[0] == "Easy":
                player.score += 10
            elif difficulty[0] == "Normal":
                player.score += 20
            elif difficulty[0] == "Hard":
                player.score += 30
            #player.score += 10
            db.session.commit()
            tf="True" #
            print("correct!")
            return redirect(url_for('trueFalse', tf=tf)) #
        else:
            tf="False" #
            print("oops!")
            return redirect(url_for('trueFalse', tf=tf)) #
        return redirect("/play_game")
    if num >= len(each_level_questions):
        return redirect("/result") 
    return render_template("play_game.html", question=each_level_questions[num], choices=choices_list[num])

@app.route("/result", methods=["GET", "POST"])
def result():
    players = Player.query.all()
    for each_player in players:
        if each_player.name == session["player_name"]:
            player = each_player
    return render_template("result.html",player=player)

@app.route("/trueFlse/<string:tf>", methods=["GET", "POST"]) #booleanの型指定の方法
def trueFalse(tf):
    return render_template("trueFalse.html", tf=tf)

if __name__ == "__main__":
    app.run(debug=True)
