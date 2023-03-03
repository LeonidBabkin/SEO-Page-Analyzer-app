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
from page_analyzer.status_validation import check_status
from page_analyzer.beautiful_soup import extract_htd


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")


app = Flask(__name__)
if __name__ == "__main__":
    app.run()
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


@app.route('/urls', methods=['GET'])  # here on the html page there's
def list_urls():  # a link 'сайты' which leads to the lst_urls.html
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute("SELECT DISTINCT ON (id) * FROM urls LEFT"
                " JOIN (SELECT url_id, status_code, created_at"
                " AS last_created FROM url_checks ORDER BY id DESC)"
                " AS checks_table"
                " ON urls.id = checks_table.url_id ORDER BY id DESC;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('lst_urls.html', records=records)


@app.route('/urls', methods=['POST'])
def hello_url():
    datum = request.form.to_dict()
    if datum['url'] == '':
        flash('URL обязателен', 'error')
        return redirect(url_for('hello_template'))
    name, date = url_entry(datum)
    if validate_url(name):
        flash('Некорректный URL', 'error')
        return render_template('index.html'), 422
    entry = check_uniqueness(name)
    if entry is not None:
        flash('Страница уже существует', 'success')
        return redirect(url_for('show_url', id=entry[0]))
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
        return redirect(url_for('show_url', id=entry[0]))


@app.route('/urls/<int:id>')
def show_url(id):
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


@app.route('/urls/<int:id>/checks', methods=['POST'])
def show_checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=NamedTupleCursor)
    cur.execute("SELECT * FROM urls WHERE id = %s", (id, ))
    top = cur.fetchone()
    try:
      status_code = check_status(top[1])
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'failure')
        return redirect(url_for('show_url', id=top[0]))
    else:
        date_check = datetime.now().strftime("%Y-%m-%d")
        h1, title, descr = extract_htd(top[1])  # extraction
        cur.execute("INSERT INTO url_checks (url_id, status_code,"
                    " h1, title, description, created_at)"
                    " VALUES (%s, %s, %s, %s, %s, %s)",
                    (top[0], status_code, h1, title, descr, date_check))
        conn.commit()
        cur.execute("SELECT * FROM url_checks WHERE url_checks.url_id = %s"
                    " ORDER BY url_checks.id DESC", (id, ))
        data = cur.fetchall()
        cur.close()
        conn.close()
        flash('Проверка прошла успешно', 'success')
        return render_template('page_tables.html',
                               id=top[0],
                               date=top[2],
                               name=top[1],
                               check_data=data)
