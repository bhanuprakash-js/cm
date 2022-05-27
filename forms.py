from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, \
    SubmitField, DateField, SelectField, IntegerRangeField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_login import current_user
from models import User_Account, User_Cooldrink


class registration_form(FlaskForm):

    def validate_username(self, username_to_check):
        user = User_Account.query.filter_by(username = username_to_check.data).first()
        if user:
            raise ValidationError('Username already exits use different name')

    def validate_email_address(self, email_address_to_check):
        if not email_address_to_check.data.endswith('.com'):
            raise ValidationError('Correct the email address pattern')
        email = User_Account.query.filter_by(email_address = email_address_to_check.data).first()
        if email:
            raise ValidationError('EmailAddress already in use try different one')
    
    def validate_tel_dtl(self, tel_dtl_to_check):
        tel_details = User_Account.query.filter_by(tel_dtl = tel_dtl_to_check.data).first()
        if tel_details:
            raise ValidationError('Phone number has been taken try different one')


    username = StringField(label='UserName:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = EmailField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6, max=18), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', 
        validators=[EqualTo('password1', message='both passwords should be the same'), DataRequired()])
    gender = SelectField(label='Gender:', validators=[DataRequired()], choices=['male', 'female', 'others'])
    date_of_birth = DateField(label='Date Of Birth:', validators=[DataRequired()])
    tel_dtl = StringField(label='Tel Number:', validators=[DataRequired()])
    submit = SubmitField(label='Register')


class signup_form(FlaskForm):
    username_or_email = StringField(label='UserName or Eamil:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='SignUp')


class add_drinks_form(FlaskForm):

    def validate_drink_name(self, drink_name_to_check):
        drink_in_ailes = User_Cooldrink.query.filter_by(drink_name = drink_name_to_check.data,
            user_id = current_user.id).first()
        if drink_in_ailes:
            raise ValidationError('Drink Already Exists! Please Try New One Instead')

    def validate_description(self, description_to_check):
        description_in_ailes = User_Cooldrink.query.filter_by(description = description_to_check.data,
            user_id = current_user.id).first()
        if description_in_ailes:
            raise ValidationError('Drinks Does not sahre the same description! try to be more specific')


    drink_name = StringField(label='Drink Name:', validators=[Length(min=2, max=250), DataRequired()])
    description = StringField(label='Description:', validators=[Length(min=10, max=500), DataRequired()])
    priority = IntegerRangeField(label='Priority:', validators=[DataRequired()])
    category = StringField(label='Category:', validators=[Length(min=4, max=100), DataRequired()])
    add_drink_btn = SubmitField(label='Add Drink', validators=[DataRequired()])


class update_drinks_form(FlaskForm):
    def validate_drink_name(self, drink_name_to_check):
        drink_in_ailes = User_Cooldrink.query.filter_by(drink_name = drink_name_to_check.data,
            user_id = current_user.id).first()
        if drink_in_ailes:
            raise ValidationError('Drink Already Exists! Please Try New One Instead')

    def validate_description(self, description_to_check):
        description_in_ailes = User_Cooldrink.query.filter_by(description = description_to_check.data,
            user_id = current_user.id).first()
        if description_in_ailes:
            raise ValidationError('Drinks Does not sahre the same description! try to be more specific')

    drink_name = StringField(label='Drink Name:', validators=[Length(min=2, max=250)])
    description = StringField(label='Description:', validators=[Length(min=10, max=500)])
    priority = IntegerRangeField(label='Priority:')
    category = StringField(label='Category:', validators=[Length(min=4, max=100)])
    update_drink_btn = SubmitField(label='Update')

class edit_values_form(FlaskForm):
    edit_values_btn = SubmitField(label='Edit Values')

class remove_drinks_form(FlaskForm):
    remove_drink_btn = SubmitField(label='Delete')


