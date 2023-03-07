import os
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import NamedTupleCursor
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_data_bits(url):
    session = requests.session()
    page = session.get(url)
    page.raise_for_status()
    status = page.status_code
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        description = soup.find(attrs={'name': 'description'})['content']
    except Exception:
        description = ''
    try:
        h1 = soup.h1.text
    except Exception:
        h1 = ''
    try:
        title = soup.title.text
    except Exception:
        title = ''
    return status, title, h1, description


def insert_into_url_checks(id, status_code, title, h1, description):
    date = datetime.now().strftime("%Y-%m-%d")
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("INSERT INTO url_checks (url_id, status_code,"
                           " title, h1, description, created_at) VALUES"
                           "(%s, %s, %s, %s,  %s, %s)",
                           (id, status_code, title, h1, description, date))
            conn.commit()
