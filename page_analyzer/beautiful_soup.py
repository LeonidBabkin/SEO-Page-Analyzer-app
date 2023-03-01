from bs4 import BeautifulSoup
import requests


def extract_htd(url):
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
    return h1, title, description
