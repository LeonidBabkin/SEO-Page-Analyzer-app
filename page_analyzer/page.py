import requests
from bs4 import BeautifulSoup


def prepare_seo_data(url):
    session = requests.session()
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) "
                             "Gecko/20100101 Firefox/60.0",
               "Accept": "text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,*/*;q=0.8"}
    page = session.get(url, headers=headers)
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
