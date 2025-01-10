from cachelib import FileSystemCache
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_session import Session
from datetime import timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)

con = sqlite3.connect('data.db', check_same_thread=False)
cursor = con.cursor()




@app.route('/')
def main_page():
    cursor.execute('select * from posts')
    data = cursor.fetchall()
    return render_template('index.html', data=data)


@app.route('/register/')
def register_page():
    return render_template('register.html')


@app.route('/save_register/', methods=['POST'])
def save_register():
    last_name = request.form['last_name']
    name = request.form['name']
    patronymic = request.form['patronymic']
    gender = request.form['gender']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    cursor.execute('insert into users (last_name,name,patronymic,gender,email,username,password) values(?,?,?,?,?,?,?)',
                   (last_name, name, patronymic, gender, email, username, password))
    con.commit()
    flash('Регистрация прошла успешно', 'success')
    return redirect(url_for('page_login'))


@app.route('/login/')
def page_login():
    return render_template('login.html')


@app.route('/authorization/', methods=['POST'])
def authorization():
    login = request.form['username']
    password = request.form['password']
    cursor.execute('select username, password from users where username=(?)', (login,))
    data = cursor.fetchall()
    if not data:
        flash('Неверный логин', 'danger')
        return redirect(url_for('page_login'))
    if password == data[0][1]:
        session['login'] = True  # флаг успешной авторизации
        session['username'] = login  # запоминаем имя пользователя который авторизовался
        session.permanent = True  # время сессии, если False, то сессия до перезапуска браузера
        # если True, то настраиваем время сессии (по умолчанию 31 день)
        app.permanent_session_lifetime = timedelta(minutes=1000)
        session.modified = True  # отвечает за передачу измененных переменных сессии от запроса к запросу

        flash('Вы успешно авторизовались', 'success')
        return redirect(url_for('main_page'))
    flash('Неверный пароль', 'danger')
    return redirect(url_for('page_login'))


@app.route('/add/')
def add_page():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('page_login'))
    return render_template('add.html')


@app.route('/save_post/', methods=['POST'])
def save_post():
    file = request.files.get('image')
    title = request.form['title']
    description = request.form['description']
    url = f'static/uploads/{file.filename}'
    file.save(url)
    cursor.execute('insert into posts (title,text, image) values (?,?,?)', (title, description, url))
    con.commit()

    flash('Пост добавлен', 'success')
    return redirect(url_for('main_page'))


@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля','danger' )
    return redirect(url_for('main_page'))

app.run(port=2000, debug=True)
