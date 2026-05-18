from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'

def format_rupiah(value):
    return f'Rp {value:,.0f}'.replace(',', '.')

app.jinja_env.filters['rupiah'] = format_rupiah
from app import routes, models