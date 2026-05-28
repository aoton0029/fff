from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_htmx import HTMX
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
htmx = HTMX()
csrf = CSRFProtect()
