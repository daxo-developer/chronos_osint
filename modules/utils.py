import random
import yaml
import stem
from stem import Signal
from stem.control import Controller

config = None

def load_config():
    global config
    if config is None:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    return config

def get_headers():
    cfg = load_config()
    return {
        'User-Agent': random.choice(cfg['user_agents']),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br'
    }

def rotate_proxy(force_new=False):
    cfg = load_config()
    if cfg['proxy']['use_tor']:
        if force_new:
            try:
                with Controller.from_port(port=9051) as controller:
                    controller.authenticate(password=cfg['proxy'].get('tor_password', ''))
                    controller.signal(Signal.NEWNYM)
                    import time
                    time.sleep(1)
            except Exception:
                pass
        return {
            'http': cfg['proxy']['http'],
            'https': cfg['proxy']['https']
        }
    return None
