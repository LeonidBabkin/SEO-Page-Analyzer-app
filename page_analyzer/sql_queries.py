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
