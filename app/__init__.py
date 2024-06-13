from flask import Flask
from .config import Config
from .models import db, bcrypt, User
from flask_login import LoginManager
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You need to be authenticated for this action'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from .routes import *

migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
