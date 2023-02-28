from bs4 import BeautifulSoup
import requests


def extract_htd(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    dismantled_tag = soup.find(attrs={'name': 'description'})
    return soup.h1.text, soup.title.text, dismantled_tag['content']
