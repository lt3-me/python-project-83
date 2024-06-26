from flask import Flask, render_template, request, flash, redirect, url_for
import os
import requests
from dotenv import load_dotenv
from .urls import validate_url, normalize_url
from .database import Database
from .html import get_seo_elements

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
db = Database(DATABASE_URL)

FLASH_MESSAGES = {
    'request_error': ('Произошла ошибка при проверке', 'error'),
    'insert_error': ('Ошибка при добавлении в базу данных', 'error'),
    'url_insert_success': ('Страница успешно добавлена', 'success'),
    'check_insert_success': ('Страница успешно проверена', 'success'),
    'url_exists': ('Страница уже существует', 'info')
}


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls_post():
    url = request.form.get('url')
    errors = validate_url(url)
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('index.html'), 422

    url = normalize_url(url)
    try:
        url_id = db.get_url_id_by_url(url)
        if url_id is None:
            url_id = db.insert_url_in_urls(url)
            flash_response('url_insert_success')
        else:
            flash_response('url_exists')

        return redirect(url_for('url_info', id=url_id))
    except ValueError:
        flash_response('insert_error')
        return render_template('index.html'), 422


@app.get('/urls')
def urls():
    urls_data = db.get_all_urls_with_latest_check_time_and_result()
    return render_template('urls/index.html', urls_data=urls_data)


@app.route('/urls/<int:id>', methods=['GET'])
def url_info(id):
    url_data = db.get_url_by_id(id)
    url_checks = db.get_url_checks_by_url_id(id)
    return render_template(
        'urls/url_info.html', id=id, url_data=url_data, url_checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    url_id, url, _ = db.get_url_by_id(id)
    try:
        r = requests.get(url=url)
        r.raise_for_status()
        status_code = r.status_code
        html_content = r.text
        h1, title, desc = get_seo_elements(html_content)
    except requests.exceptions.RequestException:
        flash_response('request_error')
    else:
        try:
            db.insert_page_check((url_id, status_code, h1, title, desc))
            flash_response('check_insert_success')
        except ValueError:
            flash_response('insert_error')

    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def flash_response(status):
    if status in FLASH_MESSAGES:
        msg, type = FLASH_MESSAGES[status]
        flash(msg, type)
