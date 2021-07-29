import os

from dotenv import load_dotenv


def name_to_snake_case(source_name) -> str:
    return '_'.join(source_name.lower().split())


def get_secret_key():
    basedir = os.path.abspath(os.path.dirname('main.py'))
    load_dotenv(os.path.join(basedir, '.env'))
    return os.getenv('SECRET_KEY')
