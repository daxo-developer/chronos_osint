import requests
import time
import random
from modules.utils import get_headers, rotate_proxy, load_config

config = load_config()
session = requests.Session()
session.proxies.update(rotate_proxy())

def search_all_engines(image_path):
    results = []
    results.extend(google_reverse_search(image_path))
    results.extend(yandex_search(image_path))
    results.extend(bing_search(image_path))
    results.extend(tineye_search(image_path))
    return list(set(results))

def safe_request(url, method='get', **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            if method.lower() == 'get':
                resp = session.get(url, headers=get_headers(), timeout=config['timeouts']['request'], **kwargs)
            else:
                resp = session.post(url, headers=get_headers(), timeout=config['timeouts']['request'], **kwargs)
            if resp.status_code == 429:
                wait = (2 ** attempt) + random.random()
                time.sleep(wait)
                continue
            if resp.status_code == 403 or 'captcha' in resp.text.lower():
                session.proxies.update(rotate_proxy(force_new=True))
                continue
            resp.raise_for_status()
            return resp
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    return None

def google_reverse_search(img_path):
    url = "https://www.google.com/searchbyimage/upload"
    files = {'encoded_image': open(img_path, 'rb')}
    resp = safe_request(url, method='post', files=files)
    if resp and resp.status_code == 302:
        return [resp.headers['Location']]
    return []

def yandex_search(img_path):
    url = "https://yandex.com/images/search"
    files = {'upfile': open(img_path, 'rb')}
    params = {'rpt': 'imageview'}
    resp = safe_request(url, method='post', files=files, params=params)
    if resp and resp.status_code == 200:
        return [resp.url]
    return []

def bing_search(img_path):
    # Требуется ключ API
    return []

def tineye_search(img_path):
    # TinEye API или прямой запроc
    return []
