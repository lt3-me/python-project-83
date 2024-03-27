from flask import Flask, render_template, request, flash, redirect, url_for
import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from .validator import validate_url
from .database import URLsDatabaseController
from .url_analysis import extract_elements_from_html

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
db = URLsDatabaseController(DATABASE_URL)

FLASH_RESPONSES = {
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
        flash_all_errors(errors)
        return render_template('index.html'), 422

    url = normalize_url(url)
    try:
        url_id = get_or_insert_url(url)
        flash_response(
            'url_insert_success' if url_id is None else 'url_exists')
        return redirect(url_for('url_info', id=url_id))
    except ValueError:
        flash_response('insert_error')
        return render_template('index.html'), 422


def get_or_insert_url(url):
    url_id = db.get_url_id_by_url(url)
    if url_id is None:
        return db.insert_url_in_urls(url)
    return url_id


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
        h1, title, desc = extract_elements_from_html(html_content)
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
    if status in FLASH_RESPONSES:
        msg, type = FLASH_RESPONSES[status]
        flash(msg, type)


def flash_all_errors(errors):
    for error in errors:
        flash(error, 'error')


def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + '://' + parsed_url.netloc
