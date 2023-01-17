import requests

def get_json_from_url(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()