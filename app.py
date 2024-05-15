from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_game.db"
app.config["SECRET_KEY"] = "secret_key"
bcrypt = Bcrypt(app)
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
    return render_template("login.html")

@app.route("/user")
def user():
    return render_template("user/index.html")

@app.route("/manager")
def manager():
    return render_template("manager/index.html")

@app.route("/login_user")
def login_user():
    return render_template("user/index.html")

"""ADMIN_PASSWORD = "adminpass"

@app.route("/login_manager", methods=["POST"])
def login_manager():
    admin_password = request.form.get("admin_password")

    if admin_password == ADMIN_PASSWORD:
        # 管理者パスワードが正しい場合は管理者ページにリダイレクト
        return render_template("manager/index.html")
    else:
        # 管理者パスワードが間違っている場合はログインページに戻り、エラーメッセージを表示
        error_message = "管理者パスワードが間違っています。"
        return render_template("login.html", error_message=error_message)*/ """

# ハッシュ化されたパスワードの保存
hashed_admin_password = "$2b$12$tmeV1huwVTxLH6.KPO7VVu8oXguCW/Uz.K1qFj7YQAhJU.oFzcndi"

@app.route("/login_manager", methods=["POST"])
def login_manager():
    admin_password = request.form.get("admin_password")

    if bcrypt.check_password_hash(hashed_admin_password, admin_password):
        # 管理者パスワードが正しい場合は管理者ページにリダイレクト
        return render_template("manager/index.html")
    else:
        # 管理者パスワードが間違っている場合はログインページに戻り、エラーメッセージを表示
        error_message = "管理者パスワードが間違ってまいす。"
        return render_template("login.html", error_message=error_message)


@app.route("/leaderboard_user")
def leaderboard_user():
    players = Player.query.order_by(Player.score.desc()).all()
    return render_template("user/leaderboard.html", players=players)

@app.route("/leaderboard_manager")
def leaderboard_manager():
     # 得点の高い順にプレイヤーを取得
    players = Player.query.order_by(Player.score.desc()).all()

    # 順位付けを行う
    ranked_players = []
    current_rank = 1
    current_score = None

    for player in players:
        if player.score != current_score:
            current_rank = len(ranked_players) + 1
        ranked_players.append((current_rank, player))
        current_score = player.score

    return render_template('manager/leaderboard.html', ranked_players=ranked_players)

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
    return render_template("user/start_game.html")

@app.route("/add_questions_user")
def add_questions_user():
    return render_template("user/add_question_form.html")

@app.route("/add_questions_manager")
def add_questions_manager():
    return render_template("manager/add_question_form.html")

@app.route("/add_question_user", methods=["POST"])
def add_question_user():
    text = request.form.get("text")
    choices = [request.form.get(f"choice{i}") for i in range(1, 5)]
    difficulty = request.form.get("difficulty")
    correct_choice = int(request.form.get("correct_choice"))

    new_question = Question(text=text, choices=",".join(choices), difficulty=difficulty, correct_choice=correct_choice)
    db.session.add(new_question)
    db.session.commit()

    return render_template("user/add_question_success.html")

@app.route("/add_question_manager", methods=["POST"])
def add_question_manager():
    text = request.form.get("text")
    choices = [request.form.get(f"choice{i}") for i in range(1, 5)]
    difficulty = request.form.get("difficulty")
    correct_choice = int(request.form.get("correct_choice"))

    new_question = Question(text=text, choices=",".join(choices), difficulty=difficulty, correct_choice=correct_choice)
    db.session.add(new_question)
    db.session.commit()

    return render_template("manager/add_question_success.html")

@app.route("/questions_user")
def list_questions():
    questions = Question.query.all() 
    return render_template("user/question_list.html", questions=questions)

@app.route("/questions_manager")
def list_questions_manager():
    questions = Question.query.all() 
    return render_template("manager/question_list.html", questions=questions)

@app.route('/delete/<int:id>')
def delete(id):
 delete_task = Question.query.get(id)
 db.session.delete(delete_task)
 db.session.commit()
 return redirect('/manager')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
 update_task = Question.query.get(id)
 if request.method == 'GET':
  return render_template('manager/question_update.html',question=update_task)
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
        return redirect("/questions_manager")
 
@app.route('/delete_player/<int:id>')
def delete_player(id):
 delete_task = Player.query.get(id)
 db.session.delete(delete_task)
 db.session.commit()
 return redirect('/manager')

@app.route('/update_player/<int:id>', methods=['GET', 'POST'])
def update_player(id):
 update_task = Player.query.get(id)
 if request.method == 'GET':
  return render_template('manager/player_update.html',player=update_task)
 if request.method == "POST":
        name = request.form.get("name")
        score = int(request.form.get("score"))

        update_task.name = name
        update_task.score = score

        db.session.commit()
        return redirect("/leaderboard_manager")


@app.route('/player_add_form')
def player_add_form():
    error_message = session.pop('error_message', None)
    return render_template('manager/player_add.html', error_message=error_message)

@app.route('/register_player', methods=['POST'])
def register_player():
    name = request.form.get('name')

    existing_player = Player.query.filter_by(name=name).first()
    if existing_player:
        error_message = 'この名前のプレイヤーは既に登録されています。別の名前を選んでください。'
        session['error_message'] = error_message
        return redirect(url_for('player_add_form'))

    # Register new player
    new_player = Player(name=name)
    db.session.add(new_player)
    db.session.commit()

    return redirect(url_for('player_add_form'))

if __name__ == "__main__":
    app.run(debug=True)
