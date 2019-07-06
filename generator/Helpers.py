from environs import Env, EnvError


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
