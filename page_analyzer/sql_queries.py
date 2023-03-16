import os
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import NamedTupleCursor
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
