import configparser

config_path = 'config.ini'
secret_path = '../secrets.ini'

def load_config():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def load_secrets():
    secrets_config = configparser.ConfigParser()
    secrets_config.read(secret_path)
    return secrets_config