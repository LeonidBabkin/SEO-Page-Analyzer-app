from flask import (Flask,
                   request,
                   redirect,
                   render_template,
                   flash, url_for)
import os
import psycopg2
import requests
from validators.url import url
from psycopg2.extras import NamedTupleCursor
from urllib.parse import urlparse
from dotenv import load_dotenv
from page_analyzer.page import get_data_bits
from page_analyzer.sql_queries import (insert_into_url_checks,
                                       select_all_sites,
                                       select_certain_site,
                                       insert_select_from_urls,
                                       select_by_id_from_urls)


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = SECRET_KEY


def validate_url(site_url):
    return not url(site_url) or len(site_url) > 255


@app.route('/')
def get_index():
    return render_template(
        'index.html')


@app.route('/urls')
def get_urls():
    site_list = select_all_sites()
    return render_template(
        'site_list.html',
        site_list=site_list)


@app.post('/urls')
def post_urls():
    parse_url = urlparse(request.form.get("url"))
    site_url = f'{parse_url.scheme}://{parse_url.hostname}'
    if validate_url(site_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422
    entry = select_certain_site(site_url)
    if entry:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=entry[0][0]))
    output = insert_select_from_urls(site_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=output[0]))


@app.post('/urls/<id>/checks')
def post_url_check(id):
    [(id, url, date)] = select_by_id_from_urls(id)
    try:
        status_code, title, h1, description = get_data_bits(url)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', id=id))
    insert_into_url_checks(id, status_code, title, h1, description)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', id=id))


@app.route('/urls/<id>')
def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE id = %s', (id,))
            [(id, name, date)] = cursor.fetchall()
            cursor.execute('SELECT * FROM url_checks WHERE url_id = %s '
                           'ORDER BY id DESC', (id,))
            site_checks = cursor.fetchall()
    return render_template(
        'single_site.html',
        id=id, name=name, date=date, site_checks=site_checks)
