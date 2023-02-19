from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
from psycopg2.extras import NamedTupleCursor


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.secret_key = SECRET_KEY


#  Open a cursor to perform database operations
def check_uniqueness(url):
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                    "SELECT * FROM urls WHERE name like %s ESCAPE ''",
                    (url,)
                    )
            return curs.fetchone()
    conn.close()


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


@app.route('/', methods=['POST'])
def hello_url():
    datum = request.form.to_dict()
    name, date = url_entry(datum)
    entry_tuple = check_uniqueness(name)
    if entry_tuple:
        pass
    else:
        with conn:
            with conn.cursor() as curs:
                curs.execute(
                        "INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                        (name, date))
        conn.close()  # leaving contexts doesn't close the connection
    return render_template('page.html', url=entry_tuple[1])
