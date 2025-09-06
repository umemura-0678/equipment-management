from flask import Flask, flash, redirect, render_template, request
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import User, Message, Item, MailMessage
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
@app.route("/user_register", methods=["GET", "POST"])
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
        return render_template("/admin/user_menu.html")

    return render_template("/admin/user_register.html")


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

    # time.sleep(3)

    return redirect("/")


# ユーザー削除処理
@app.route("/unregister")
def unregister():
    current_user.delete_instance()
    logout_user()
    return redirect("/")


# メッセージ投稿フォームの表示・投稿
@app.route("/mess", methods=["GET", "POST"])
def mess():
    if request.method == "POST" and current_user.is_authenticated:
        Message.create(user=current_user, content=request.form["content"])

    messages = (
        Message.select()
        .where(Message.reply_to.is_null(True))
        .order_by(Message.pub_date.desc(), Message.id.desc())
    )
    return render_template("/select_item/message.html", messages=messages)


# 予約処理
@app.route("/select/s1_video_camera", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        # データの検証
        if not request.form["start_day"] or not request.form["end_day"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        Item.create(
            # item_name=request.form["item_name"],
            item_name="ビデオカメラ",
            start_date=request.form["start_day"],
            end_date=request.form["end_day"],
            # status=request.form["status"],
            status="予約中",
            user=current_user,
        )
        return render_template("/select.html")
    return render_template("/select_item/s1_video_camera.html")


# 管理画面ログイン機能
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if not request.form["password"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # ここでユーザーを認証し、OKならログインする
        user = User.select().where(User.name == "admin").first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")

            return redirect("/admin_menu")

        # NGならフラッシュメッセージを設定
        flash("認証に失敗しました")

    return render_template("/admin/admin_login.html")


# すべてのユーザーへメール送信
@app.route("/mail_send")
def mail_send():
    if request.method == "POST":
        MailMessage.create(user=current_user, content=request.form["content"])
    mail_messages = MailMessage.select().order_by(MailMessage.pub_date.desc(), MailMessage.id.desc())
    return render_template("/admin/mail_send.html", mail_messages=mail_messages)
    # return render_template("/admin/mail_send.html")


@app.route("/admin_menu")
def admin_menu():
    return render_template("/admin/admin_menu.html")


# @app.route("/user_register")
# def user_register():
#     return render_template("/admin/user_register.html")
@app.route("/user_delete")
def user_delete():
    return render_template("/admin/user_delete.html")


@app.route("/item_register")
def item_register():
    return render_template("/admin/item_register.html")


@app.route("/item_delete")
def item_delete():
    return render_template("/admin/item_delete.html")





@app.route("/user_menu")
def user_menu():
    return render_template("/admin/user_menu.html")


@app.route("/item_menu")
def item_menu():
    return render_template("/admin/item_menu.html")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/select")
def select():
    return render_template("select.html")


@app.route("/select/s1_video_camera")
def video_camera():
    return render_template("/select_item/s1_video_camera.html")


@app.route("/select/s2_speaker")
def speaker():
    return render_template("/select_item/s2_speaker.html")


@app.route("/select/s3_video_deck")
def video_deck():
    return render_template("/select_item/s3_video_deck.html")


@app.route("/select/s4_tv")
def tv():
    return render_template("/select_item/s4_tv.html")


@app.route("/select/s5_refrigerator")
def refrigerator():
    return render_template("/select_item/s5_refrigerator.html")


@app.route("/select/s6_laundry_machine")
def laundry_machine():
    return render_template("/select_item/s6_laundry_machine.html")


@app.route("/select/s7_microwave")
def microwave():
    return render_template("/select_item/s7_microwave.html")


@app.route("/select/s8_rice_cooker")
def rice_cooker():
    return render_template("/select_item/s8_rice_cooker.html")


@app.route("/select/s9_hair_dryer")
def hair_dryer():
    return render_template("/select_item/s9_hair_dryer.html")


@app.route("/select/s10_air_conditioner")
def air_conditioner():
    return render_template("/select_item/s10_air_conditioner.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
