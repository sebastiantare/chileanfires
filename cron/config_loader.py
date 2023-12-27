import os
import configparser

script_dir = os.path.dirname(os.path.abspath(__name__))

config_path = os.path.join(script_dir, 'config.ini')
secret_path = os.path.join(script_dir, '../secrets.ini')

def load_config():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def load_secrets():
    secrets_config = configparser.ConfigParser()
    secrets_config.read(secret_path)
    return secrets_config