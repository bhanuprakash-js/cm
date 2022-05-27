from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cdData.db'
app.config['SECRET_KEY'] = '4293d86cd206e25331119c1ebfa3b2'

db = SQLAlchemy(app)

flask_bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

import routes
