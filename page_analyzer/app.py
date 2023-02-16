from flask import Flask, render_template, request
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor
import datetime


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = SECRET_KEY


conn = psycopg2.connect('postgresql://leonid:babkin36@host:5432/page_analyzer')


@app.route("/")
def hello_template():
    data = {'url': ''}
    return render_template('index.html', data=data)


@app.route('/', methods=['POST'])
def hello_url():
    datum = request.form.to_dict()
    url = datum['url']
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        cusr.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)", (site_url, datetime.time))
    cursor.close()
    conn.close()
    return render_template('page.html', url=url)
