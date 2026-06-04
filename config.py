import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'superkey123'
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://postgres:postgresql17@localhost:5432/inventory_app"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REGISTER_TOKEN = os.environ.get('REGISTER_TOKEN') or 'supertoken123'