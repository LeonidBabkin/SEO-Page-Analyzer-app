from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages)
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import NamedTupleCursor
from page_analyzer.validation import validate_url


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.secret_key = SECRET_KEY


def check_uniqueness(url):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute("SELECT * FROM urls WHERE name like %s ESCAPE ''",
                (url,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res


def url_entry(datum):
    datum = request.form.to_dict()
    raw_url = urlparse(datum['url'])
    whole_url = f'{raw_url.scheme}://{raw_url.hostname}'
    date = datetime.now().strftime("%Y-%m-%d")
    return whole_url, date


@app.route("/")
def hello_template():
    data = {'url': ''}
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', data=data, messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def hello_url():
    if request.method == 'POST':
        datum = request.form.to_dict()

        if datum['url'] == '':
            flash('URL обязателен', 'error')
            return redirect(url_for('hello_template'))

        name, date = url_entry(datum)
        valid_res = validate_url(name)

        if valid_res is not None:
            flash(valid_res, 'error')
            return redirect(url_for('hello_template'))

        entry = check_uniqueness(name)
        if entry is not None:
            flash('Страница уже существует', 'success')
            return redirect(url_for('get_url', id=entry[0]))

        if entry is None:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor(cursor_factory=NamedTupleCursor)
            cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                        (name, date))
            conn.commit()
            cur.close()
            conn.close()
            entry = check_uniqueness(name)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('get_url', id=entry[0]))
    if request.method == 'GET':
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=NamedTupleCursor)
        cur.execute("SELECT * FROM urls ORDER BY id DESC")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('lst_urls.html', records=records)


@app.route('/urls/<int:id>')
def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute("SELECT * FROM urls WHERE id = %s", (id, ))
    entry = cur.fetchone()
    cur.close()
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template('page_tables.html',
                           id=entry[0],
                           name=entry[1],
                           date=entry[2],
                           messages=messages)
