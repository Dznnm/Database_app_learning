import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'superkey123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REGISTER_TOKEN = os.environ.get('REGISTER_TOKEN') or 'supertoken123'