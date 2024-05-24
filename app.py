from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random
from sqlalchemy import func
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
    explain = db.Column(db.Text, nullable=True)

error_message=""
@app.route("/")
def index():
    global error_message
    error_message=""
    return render_template("index.html")

@app.route("/user")
def user():
    global error_message
    error_message=""
    return render_template("user/top.html")

@app.route("/manager")
def manager():
    return render_template("manager/top.html")

@app.route("/login_user")
def login_user():
    return render_template("user/top.html")

# ハッシュ化されたパスワードの保存
hashed_admin_password = "$2b$12$tmeV1huwVTxLH6.KPO7VVu8oXguCW/Uz.K1qFj7YQAhJU.oFzcndi"

@app.route("/login_manager", methods=["POST"])
def login_manager():
    admin_password = request.form.get("admin_password")

    if bcrypt.check_password_hash(hashed_admin_password, admin_password):
        # 管理者パスワードが正しい場合は管理者ページにリダイレクト
        return render_template("manager/top.html")
    else:
        # 管理者パスワードが間違っている場合はログインページに戻り、エラーメッセージを表示
        error_message = "管理者パスワードが間違ってまいす。"
        return render_template("index.html", error_message=error_message)


@app.route("/leaderboard_user")
def leaderboard_user():
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
    return render_template("user/leaderboard.html", ranked_players=ranked_players)

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

id = 0
new_re=0
@app.route("/start_game", methods=["GET", "POST"])
def start_game():
    if request.method == "POST":
        global error_message
        error_message = ""
        if request.form.get('new_name') != "":
            global new_re
            new_re=0
            name = request.form.get('new_name')

            existing_player = Player.query.filter_by(name=name).first()
            if existing_player:
                error_message = 'この名前のプレイヤーは既に登録されています。別の名前を選んでください。'
                #session['error_message'] = error_message
                #error_message = session.pop('error_message', None)
                return redirect("/start_game")

            # Register new player
            new_player = Player(name=name)
            db.session.add(new_player)
            session["player_name"] = name
            db.session.commit()
        else:
            name = request.form.get('name')
            new_re=1
            existing_player = Player.query.filter_by(name=name).first()
            if not existing_player:
                error_message = 'この名前のプレイヤーは未登録です。'
                return redirect("/start_game")
            session["player_name"] = name
            db.session.commit()
        return redirect("/select_difficulty")
    return render_template("user/start_game.html", error_message=error_message)
   

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
    explain = request.form.get("explain")

    new_question = Question(text=text, choices=",".join(choices), difficulty=difficulty, correct_choice=correct_choice, explain=explain)
    db.session.add(new_question)
    db.session.commit()

    return render_template("user/add_question_success.html")

@app.route("/add_question_manager", methods=["POST"])
def add_question_manager():
    text = request.form.get("text")
    choices = [request.form.get(f"choice{i}") for i in range(1, 5)]
    difficulty = request.form.get("difficulty")
    correct_choice = int(request.form.get("correct_choice"))
    explain = request.form.get("explain")

    new_question = Question(text=text, choices=",".join(choices), difficulty=difficulty, correct_choice=correct_choice, explain=explain)
    db.session.add(new_question)
    db.session.commit()

    return render_template("manager/add_question_success.html")

@app.route("/questions_user")
def list_questions():
    questions = Question.query.all() 
    number = 0
    numque =[]
    for question in questions:
        number = number + 1
        numque.append((number,question))
    return render_template("user/question_list.html", numque=numque)

@app.route("/questions_manager")
def list_questions_manager():
    questions = Question.query.all() 
    number = 0
    numque =[]
    for question in questions:
        number = number + 1
        numque.append((number,question))
    return render_template("manager/question_list.html", numque=numque)

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
        explain = request.form.get("explain")

        update_task.text = text
        update_task.choices = ",".join(choices)
        update_task.difficulty = difficulty
        update_task.correct_choice = correct_choice
        update_task.explain = explain

        db.session.commit()
        return redirect("/questions_manager")

num = 0
@app.route("/select_difficulty", methods=["GET", "POST"])
def select_difficulty_decision():
    if request.method == "POST":
        session["difficulty"] = request.form
        global num
        num = 0
        return redirect("/play_game")
    return render_template("user/select_difficulty.html")


each_level_questions = []
choices_list = []
pre_score = 0
@app.route("/play_game", methods=["GET", "POST"])
def play_game():
    global num
    global each_level_questions
    global choices_list
    difficulty = list(session.get("difficulty").values())
    print(num)
    if num == 0 and request.method == "GET":
        each_level_questions = []
        choices_list = []
        questions = Question.query.all()
        for question in questions:
            if question.difficulty == difficulty[0]:
                each_level_questions.append(question)
        print(each_level_questions)
        random.shuffle(each_level_questions)
        print(each_level_questions)
        for question in each_level_questions:
            choices_list.append(question.choices.split(","))
    print(each_level_questions)
    print(choices_list)
    #question = Question.query.filter_by(Question.query.difficulty==difficulty[0])

    # if num >= len(each_level_questions):
    if num >= len(each_level_questions):
        return redirect("/result")
    if request.method == "POST": 
        selected_choice = []
        tf="False"
        #selected_choice = int(request.form.values()[0])
        selected_choice.append(request.form.get("1"))
        selected_choice.append(request.form.get("2"))
        selected_choice.append(request.form.get("3"))
        selected_choice.append(request.form.get("4"))
        print(selected_choice)
        print(each_level_questions[num].correct_choice)
        print(selected_choice[each_level_questions[num].correct_choice-1])
        print(selected_choice[each_level_questions[num].correct_choice-1] == str(each_level_questions[num].correct_choice))
        players = Player.query.all()
        for each_player in players:
            if each_player.name == session["player_name"]:
                player = each_player
        if num == 0:
            global pre_score
            pre_score = player.score
            player.score=0
        if selected_choice[each_level_questions[num].correct_choice-1] == str(each_level_questions[num].correct_choice):
            #player = Player.query.filter_by(name=session["player_name"]).first()
            if difficulty[0] == "Easy":
                player.score += 10
            elif difficulty[0] == "Normal":
                player.score += 20
            elif difficulty[0] == "Hard":
                player.score += 30
            #player.score += 10
            db.session.commit()
            tf="True" 
            print("correct!")
            print(num)
            correct_choice_text = choices_list[num][each_level_questions[num].correct_choice - 1]
            num += 1
            return redirect(url_for('trueFalse', tf=tf, correct=correct_choice_text)) 
        else:
            tf="False" 
            print(num)
            print("oops!")
            correct_choice_text = choices_list[num][each_level_questions[num].correct_choice - 1]
            num += 1
            return redirect(url_for('trueFalse', tf=tf, correct=correct_choice_text)) 
    return render_template("user/play_game.html", question=each_level_questions[num], choices=choices_list[num])

@app.route("/result", methods=["GET", "POST"])
def result():
    # プレイヤーのスコアを取得
    player = Player.query.filter_by(name=session["player_name"]).first()
    # 順位を計算
    global pre_score
    save_pre_score = pre_score
    save_this_score = player.score
    # スコアが高い他のプレイヤーの数をカウント
    higher_score_count = Player.query.filter(Player.score > player.score).count()
    rank = higher_score_count + 1
    if pre_score > player.score:
        player.score = pre_score
        db.session.commit()

    global new_re
    return render_template("user/result.html", player=player, rank=rank, save_pre_score=save_pre_score, new_re=new_re, save_this_score=save_this_score)

@app.route("/trueFlse/<string:tf>", methods=["GET", "POST"]) #booleanの型指定の方法
def trueFalse(tf):
    correct = request.args.get('correct')
    explanation = each_level_questions[num - 1].explain
    return render_template("user/trueFalse.html", tf=tf, explanation=explanation, question=each_level_questions[num - 1], correct=correct)
 
@app.route('/delete_player/<int:id>')
def delete_player(id):
 delete_task = Player.query.get(id)
 db.session.delete(delete_task)
 db.session.commit()
 return redirect('/manager')

    

if __name__ == "__main__":
    app.run(debug=True)
