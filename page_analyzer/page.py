import requests
from bs4 import BeautifulSoup


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
