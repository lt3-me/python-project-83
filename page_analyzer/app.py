from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import os
from dotenv import load_dotenv
from .validator import validate_url

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST', 'GET'])
def urls():
    if request.method == 'POST':
        url = request.form['url']
        if validate_url(url):
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM urls WHERE name = %s LIMIT 1", (url,))
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(
                        "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                        (url,))
                    conn.commit()
                    id = cursor.fetchone()[0]
                    print(f'Page {url} added')
                    flash('Страница успешно добавлена', 'success')
                else:
                    id = exists[0]
                    flash('Страница уже существует', 'info')

                cursor.close()
                conn.close()
                return redirect(url_for('url_info', id=id))

            except psycopg2.Error:
                print(psycopg2.Error)
                conn.rollback()
                flash('Ошибка при добавлении в базу данных', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('urls'))
        else:
            flash('Некорректный URL', 'error')
            return redirect(url_for('index'))
    else:
        return render_template('urls/index.html')


@app.route('/urls/<int:id>', methods=['GET'])
def url_info(id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM urls WHERE id = %s LIMIT 1", (id,))
    url_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('urls/url_info.html', id=id, url_data=url_data)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    pass
