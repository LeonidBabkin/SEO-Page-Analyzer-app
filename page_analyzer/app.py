from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import NamedTupleCursor


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.secret_key = SECRET_KEY


#  Open a cursor to perform database operations
def check_uniqueness(url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                    "SELECT * FROM urls WHERE name like %s ESCAPE ''",
                    (url,)
                    )
            return curs.fetchone()


def url_entry(datum):
    datum = request.form.to_dict()
    url = urlparse(datum['url'])
    name = f'{url.scheme}://{url.hostname}'
    date = datetime.now().strftime("%Y-%m-%d")
    return name, date


@app.route("/")
def hello_template():
    data = {'url': ''}
    return render_template('index.html', data=data)


@app.route('/urls', methods=['POST'])
def hello_url():
    conn = psycopg2.connect(DATABASE_URL)
    datum = request.form.to_dict()
    name, date = url_entry(datum)
    entry = check_uniqueness(name)
    print('entry1:', entry)
    if entry is not None:
        flash('Страница уже добавлена')
        return redirect(url_for('get_url', id=entry[0]))
    else:
        with conn:
            with conn.cursor() as curs:
                curs.execute(
                        "INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                        (name, date))
        entry = check_uniqueness(name)
        print('entry2:', entry)
        flash('Страница успешно добавлена')
        return redirect(url_for('get_url', id=entry[0]))


@app.route('/urls/<int:id>')
def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                    "SELECT * FROM urls WHERE id = %s",
                    (id,)
                    )
            entry = curs.fetchone()
    messages = get_flashed_messages(with_categories=True)
    conn.close()
    return render_template(
            'page_tables.html',
            id=entry[0],
            name=entry[1],
            date=entry[2],
            messages=messages,
            )
