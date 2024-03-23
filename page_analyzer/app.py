from flask import Flask, render_template, request, flash, redirect, url_for
import os
from dotenv import load_dotenv
from .validator import validate_url
from .database import URLsDatabaseController

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
db = URLsDatabaseController(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    if not validate_url(url):
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'))

    id, status = db.try_insert_url_in_urls(url)
    flash_response(status)
    return redirect(url_for('url_info', id=id))


@app.get('/urls')
def urls():
    urls_data = db.get_all_urls_with_latest_check_time_and_result()
    return render_template('urls/index.html', urls_data=urls_data)


@app.route('/urls/<int:id>', methods=['GET'])
def url_info(id):
    url_data = db.get_url_data_for_id(id)
    url_checks = db.get_all_url_checks_for_url_id(id)
    return render_template(
        'urls/url_info.html', id=id, url_data=url_data, url_checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    status = db.try_check_url_by_id(id)
    flash_response(status)
    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def flash_response(status):
    flash_responses = {
        'request_error': ('Произошла ошибка при проверке', 'error'),
        'insert_error': ('Ошибка при добавлении в базу данных', 'error'),
        'success': ('Страница успешно добавлена', 'success'),
        'check_success': ('Страница успешно проверена', 'success'),
        'exists': ('Страница уже существует', 'info')
    }
    if status in flash_responses:
        msg, type = flash_responses[status]
        flash(msg, type)
