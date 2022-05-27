from importer import db, flask_bcrypt, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_account_id):
    return User_Account.query.get(int(user_account_id))


class User_Account(db.Model, UserMixin):
    __tablename__ = 'users_accounts'

    id = db.Column('id', db.Integer(), primary_key = True)
    username = db.Column('user_name', db.String(250), nullable = False, unique = True)
    email_address = db.Column('email_address', db.String(500), nullable = False, unique = True)
    password_hash = db.Column('user_password', db.String(500), nullable = False)
    gender = db.Column('user_gender', db.String(100), nullable = False)
    date_of_birth = db.Column('user_dob', db.Date(), nullable = False)
    tel_dtl = db.Column('user_telephone', db.String(13), nullable = False, unique = True) 
    created_date = db.Column('created_on', db.DateTime(), server_default = db.func.current_timestamp())

    user_drinks = db.relationship(
        'User_Cooldrink',
        backref = 'users_accounts',
        lazy = 'dynamic'
    )

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = flask_bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return flask_bcrypt.check_password_hash(self.password_hash, attempted_password)


class User_Cooldrink(db.Model):
    __tablename__ = 'user_cooldrinks'

    id = db.Column('id', db.Integer(), primary_key = True)
    drink_name = db.Column('drink', db.String(250), nullable = True)
    description = db.Column('drink_description', db.String(500), nullable = False)
    priority = db.Column('drink_priority', db.Integer(), nullable = False)
    category = db.Column('drink_category', db.String(100), default = 'beverage')
    added_on = db.Column('created_on', db.DateTime(), default = datetime.utcnow())
    last_updated = db.Column('last_updated_on', db.DateTime(), default = datetime.utcnow())

    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('users_accounts.id'), nullable = False)

