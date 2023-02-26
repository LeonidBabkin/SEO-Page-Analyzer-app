import requests


def check_status(url):
    try:
        response = requests.get(url)
        return response.status_code
    except Exception:
        return 'Произошла ошибка при проверке'
