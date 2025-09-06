from flask import Flask, flash, redirect, render_template, request
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import User, Message, Item, MailMessage
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


# すべてのユーザーへメール送信
@app.route("/mail_send", methods=["GET", "POST"])
def mail_send():
    if request.method == "POST" and current_user.is_authenticated:
        content = request.form["content"]
        subject = "お知らせ"  # メールの件名

        # メッセージをデータベースに保存
        MailMessage.create(user=current_user, content=content)

        # 全ユーザーのemailリストを取得
        user_email_list = get_user_email_list_efficient()

        # 各ユーザーにメール送信
        if user_email_list:
            success = send_email_to_users(user_email_list, subject, content)
            if success:
                flash("メール送信が完了しました。")
            else:
                flash("メール送信に失敗しました。")
        else:
            flash("送信先のユーザーが見つかりません。")

    mail_messages = (
        MailMessage.select()
        .where(MailMessage.reply_to.is_null(True))
        .order_by(MailMessage.pub_date.desc(), MailMessage.id.desc())
    )
    return render_template("/admin/mail_send.html", mail_messages=mail_messages)


# ユーザーのemailリストを取得する関数
def get_user_email_list():
    """usersテーブルからemailのリストを作成する"""
    email_list = []
    for user in User.select():
        email_list.append(user.email)
    return email_list


# より効率的な方法（リスト内包表記を使用）
def get_user_email_list_efficient():
    """usersテーブルからemailのリストを作成する（効率的な方法）"""
    return [user.email for user in User.select()]


# 特定の条件でemailリストを取得する例
def get_user_email_list_by_condition():
    """特定の条件でemailリストを取得する例"""
    # 例：admin以外のユーザーのemailリスト
    return [user.email for user in User.select().where(User.name != "admin")]


# メール送信機能
def send_email_to_users(email_list, subject, content):
    """email_listの各要素にメールを送信する"""
    # SMTPサーバーの設定（Gmailの場合）
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "yume067829@gmail.com"  # 送信者のメールアドレス
    sender_password = "your-app-password"  # アプリパスワード

    try:
        # SMTPサーバーに接続
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # 各メールアドレスに送信
        for recipient_email in email_list:
            # メールの作成
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject

            # メール本文の追加
            msg.attach(MIMEText(content, "plain", "utf-8"))

            # メール送信
            server.send_message(msg)
            print(f"メール送信完了: {recipient_email}")

        server.quit()
        return True

    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


# 予約処理
@app.route("/select/s1_video_camera", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        # データの検証
        if not request.form["start_day"] or not request.form["end_day"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # 日付文字列から日付部分を抽出
        start_day_str = request.form["start_day"]
        end_day_str = request.form["end_day"]
        print(start_day_str, end_day_str)

        # 日付文字列をdatetimeオブジェクトに変換（形式に応じて調整）
        # 例: "2024-01-15" 形式の場合
        start_date = datetime.strptime(start_day_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_day_str, "%Y-%m-%d").date()
        print(start_date, end_date)



        reserve_calendar = []
        #for item in Item.select():
        if Item.select().where(Item.item_name == "ビデオカメラ").exists():

            print("ビデオカメラがあります")
            for item in Item.select():
                if item.item_name == "ビデオカメラ":
                    # データベースの日付も同様に処理
                    item_start = datetime.strptime(str(item.start_date), "%Y-%m-%d").date()
                    item_end = datetime.strptime(str(item.end_date), "%Y-%m-%d").date()
                    print(item_start, item_end)

                    for m in range((item_end - item_start).days + 1):
                        reserve_calendar.append(item_start + timedelta(days=m))
                    # 重複を削除
                    reserve_calendar = list(dict.fromkeys(reserve_calendar))
                    print(reserve_calendar)

            form_start = datetime.strptime(str(start_date), "%Y-%m-%d").date()
            form_end = datetime.strptime(str(end_date), "%Y-%m-%d").date()

            flag = 0
            for k in range((form_end - form_start).days + 1):
                k2 = form_start + timedelta(days=k)
                if k2 in reserve_calendar:
                    # flash("その日はすでに予約されています。")
                    flag = 1
                    # return redirect(request.url)

            if flag == 0:
                flash("予約できました。")

                Item.create(
                        # item_name=request.form["item_name"],
                        item_name="ビデオカメラ",
                        start_date=request.form["start_day"],
                        end_date=request.form["end_day"],
                        # status=request.form["status"],
                        status="予約中",
                        user=current_user,
                    )
                return redirect(request.url)    
            else:
                flash("その日はすでに予約されています。")
                return redirect(request.url)

        else:
            print("ビデオカメラがありません")
            Item.create(
                        # item_name=request.form["item_name"],
                        item_name="ビデオカメラ",
                        start_date=request.form["start_day"],
                        end_date=request.form["end_day"],
                        # status=request.form["status"],
                        status="予約中",
                        user=current_user,
                    
                )
            print("ビデオカメラを登録しました")
            return redirect(request.url)

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
