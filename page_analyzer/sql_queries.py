import os
import psycopg2
from datetime import datetime
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


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

          
def select_all_sites():
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("SELECT DISTINCT ON (id) * FROM urls LEFT"
                           " JOIN (SELECT url_id, status_code,"
                           " created_at AS last_check_date FROM"
                           " url_checks ORDER BY id DESC) AS checks ON"
                           " urls.id = checks.url_id ORDER BY id DESC;")
            site_list = cursor.fetchall()
            return site_list
