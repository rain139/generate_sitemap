from environs import Env, EnvError
from urllib.request import urlopen

def env(key: str, default: str = None) -> str:
    env = Env()
    env.read_env()
    try:
        return env(key)
    except EnvError:
        if default:
            return default
        else:
            exit('Not find {key} in .env'.format(key=key))

def send_telegram(text:str)-> None:
    urlopen(
        'https://api.telegram.org/bot740828408:AAHHPyrSCmwy9jBO8uCr76ogd1lW2bWpIyw/sendMessage?chat_id=406873185&text={text}'.format(
            text=text)
    )