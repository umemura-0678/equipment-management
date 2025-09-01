from flask import Flask, flash, redirect, render_template,request
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import User
import time

app = Flask(__name__)
app.secret_key = "secret"
login_manager = LoginManager()
login_manager.init_app(app)


# Flask-Loginがユーザー情報を取得するためのメソッド
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# ユーザー登録フォームの表示・登録処理
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # データの検証
        if not request.form["name"] or not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります。")
            return redirect(request.url)
        if User.select().where(User.name == request.form["name"]):
            flash("その名前はすでに使われています。")
            return redirect(request.url)
        if User.select().where(User.email == request.form["email"]):
            flash("そのメールアドレスはすでに使われています。")
            return redirect(request.url)

        # ユーザー登録
        User.create(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
        )
        return render_template("index.html")

    return render_template("register.html")


# ログインフォームの表示・ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # ここでユーザーを認証し、OKならログインする
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            
            return redirect("/select")

        # NGならフラッシュメッセージを設定
        flash("認証に失敗しました")

    return render_template("login.html")


# ログアウト処理
@app.route("/logout")
def logout():
    logout_user()
    flash("ログアウトしました！")
    return redirect("/")


# ユーザー削除処理
@app.route("/unregister")
def unregister():
    current_user.delete_instance()
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select")
def select():
    return render_template("select.html")

@app.route("/select/s1_video_camera")
def video_camera():
    return render_template("/select_list/s1_video_camera.html")

@app.route("/select/s2_speaker")
def speaker():
    return render_template("/select_list/s2_speaker.html")

@app.route("/select/s3_video_deck")
def video_deck():
    return render_template("/select_list/s3_video_deck.html")

@app.route("/select/s4_tv")
def tv():
    return render_template("/select_list/s4_tv.html")

@app.route("/select/s5_refrigerator")
def refrigerator():
    return render_template("/select_list/s5_refrigerator.html")

@app.route("/select/s6_laundry_machine")
def laundry_machine():
    return render_template("/select_list/s6_laundry_machine.html")

@app.route("/select/s7_microwave")
def microwave():
    return render_template("/select_list/s7_microwave.html")

@app.route("/select/s8_rice_cooker")
def rice_cooker():
    return render_template("/select_list/s8_rice_cooker.html")

@app.route("/select/s9_hair_dryer")
def hair_dryer():
    return render_template("/select_list/s9_hair_dryer.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
