from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
def format_rupiah(value):
    return f'Rp {value:,.0f}'.replace(',', '.')

app.jinja_env.filters['rupiah'] = format_rupiah

def format_qty(qty, satuan):
    if satuan == 'gram' and qty >= 1000:
        return f"{qty/1000:.2f} kg"
    elif satuan == 'ml' and qty >= 1000:
        return f"{qty/1000:.2f} liter"
    return f"{qty:g} {satuan}"

app.jinja_env.filters['format_qty'] = format_qty
from app import routes, models