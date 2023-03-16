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
    cursor.close()
    conn.close()


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
    cursor.close()
    conn.close()
    return site_list


def select_certain_site(site_url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name = %s', (site_url,))
            entry = cursor.fetchall()
    cursor.close()
    conn.close()
    return entry


def insert_select_from_urls(site_url):
    date = datetime.now().strftime("%Y-%m-%d")
    conn = psycopg2.connect(DATABASE_URL)
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("INSERT INTO urls (name, created_at) "
                           "VALUES (%s, %s)", (site_url, date))
            conn.commit()
            cursor.execute('SELECT id FROM urls WHERE name = %s', (site_url,))
            output = cursor.fetchall()            
    cursor.close()
    conn.close()
    return output
