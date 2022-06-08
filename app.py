from enum import unique
from flask import Flask
from flask import render_template, request, redirect
#ModuleNotFoundError: No module namedの対応
import sys
sys.path.append('/Users/aoisawa/project/py-flask-app2/env/lib/python3.10/site-packages')
from flask_sqlalchemy import SQLAlchemy
#ログイン機能
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
#passwordのハッシュ化および確認
from werkzeug.security import generate_password_hash, check_password_hash
import os
#Bootstrap適用
from flask_bootstrap import Bootstrap

#タイムゾーン設定
from datetime import datetime
import pytz

#インスタンス生成&app連携
app = Flask(__name__)
#DB設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
#暗号化の設定
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

#クラスPost定義
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

#クラスUser定義
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)

#ユーザーのログイン状態を取得
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

#TOP
@app.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    #GETの処理
    if request.method == 'GET':
        #全てのデータをpostsへ代入
        posts = Post.query.order_by(Post.created_at.desc()).all()
        #postsの有効化
        return render_template('index.html', posts=posts)

#ユーザー登録
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #POSTの処理
    if request.method == 'POST':
        #createのformから値を取得
        username = request.form.get('username')
        password = request.form.get('password')
        #Userをインスタンス化→取得した値を代入→user作成
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        #DBへuserを追加
        db.session.add(user)
        #DBへ反映
        db.session.commit()
        #TOPへリダイレクト
        return redirect('/login')
    #GETの処理
    else:
        return render_template('signup.html')

#ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    #POSTの処理
    if request.method == 'POST':
        #loginのformから値を取得
        username = request.form.get('username')
        password = request.form.get('password')
        #usernameを検索して値を取得
        user = User.query.filter_by(username=username).first()
        #passwordが合致しているか確認
        if check_password_hash(user.password, password):
            login_user(user)
        #TOPへリダイレクト
            return redirect('/')
    #GETの処理
    else:
        return render_template('login.html')

#ログアウト:ログインしているユーザーのみ閲覧可
@app.route('/logout')
# @login_required
def logout():
    logout_user()
    return redirect('/login')

#新規登録
@app.route('/create', methods=['GET', 'POST'])
# @login_required
def create():
    #POSTの処理
    if request.method == 'POST':
        #createのformから値を取得
        title = request.form.get('title')
        body = request.form.get('body')
        #Postをインスタンス化→取得した値を代入→post作成
        post = Post(title=title, body=body)
        #DBへpostを追加
        db.session.add(post)
        #DBへ反映
        db.session.commit()
        #TOPへリダイレクト
        return redirect('/')
    #GETの処理
    else:
        return render_template('create.html')

#更新
@app.route('/<int:id>/update', methods=['GET', 'POST'])
# @login_required
def update(id):
    #選択されたidのpostを取得
    post = Post.query.get(id)
    #GETの処理
    if request.method == 'GET':
        return render_template('update.html', post=post)
    #POSTの処理
    else:
        #updateのformから値を取得
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        #DBへ反映
        db.session.commit()
        #TOPへリダイレクト
        return redirect('/')

#削除
@app.route('/<int:id>/delete', methods=['GET', 'POST'])
# @login_required
def delete(id):
    #選択されたidのpostを取得
    post = Post.query.get(id)
    #GETの処理
    if request.method == 'GET':
        return render_template('delete.html', post=post)
    #POSTの処理
    else:
        #DBから削除
        db.session.delete(post)
        #DBへ反映
        db.session.commit()
        #TOPへリダイレクト
        return redirect('/')
