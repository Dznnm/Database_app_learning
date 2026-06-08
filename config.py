import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is missing")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REGISTER_TOKEN = os.environ.get('REGISTER_TOKEN')