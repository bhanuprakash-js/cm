from sqlite3 import OperationalError
from importer import app, db
from flask import render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from forms import registration_form, signup_form, add_drinks_form, \
    remove_drinks_form, update_drinks_form, edit_values_form
from models import User_Account, User_Cooldrink
from requests import get
from datetime import datetime
from phonenumbers.phonenumberutil import country_code_for_region


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/registration', methods=['GET', 'POST'])
def register_page():

    current_country_phone_code =''
    current_tel_input_maxlength=15
    phone_number_error = ''

    try:
        country_name = get('https://ipinfo.io/country').text.split('\n')[0].replace(' ', '')
        current_country_phone_code = '+'+str(country_code_for_region(country_name))
        current_tel_input_maxlength = len(current_country_phone_code) + 10
    except Exception as e:
        phone_number_error = 'type country code manually with leading + since you are offline'

    register_form = registration_form()

    if register_form.validate_on_submit():

        user_to_create = User_Account(username=register_form.username.data,
                                    email_address=register_form.email_address.data,
                                    gender = register_form.gender.data,
                                    date_of_birth = register_form.date_of_birth.data,
                                    tel_dtl = register_form.tel_dtl.data,
                                    password = register_form.password1.data
                                    )

        db.session.add(user_to_create)
        db.session.commit()     

        if current_user.is_authenticated: 
           logout_user()

        login_user(user_to_create) 

        flash(f'Account created successfully! you are now logged in as \
            {user_to_create.username}', category='success')                     
        return redirect(url_for('ailes_home_page'))
    
    if register_form.errors != {}:
        for err_msg in register_form.errors.values():
            flash(f'ther was an error creating an account : {err_msg[0]}', category='danger')

    return render_template('registration.html', register_form = register_form, 
        country_code = current_country_phone_code,
        maxlength_of_tel_in = current_tel_input_maxlength,
        phone_number_error = phone_number_error)

@app.route('/login', methods=['GET', 'POST'])
def login_page():

    login_form = signup_form()

    if login_form.validate_on_submit():

        form_to_string = str(login_form.username_or_email.data)

        if form_to_string.endswith('.com'):#username authentic login
            attempted_email = User_Account.query.filter_by(email_address = login_form.username_or_email.data).first()

            if attempted_email and attempted_email.check_password_correction(
                attempted_password = login_form.password.data):

                login_user(attempted_email)
                flash(f'success! You are logged in as {attempted_email.username}', 
                    category='success')

                return redirect(url_for('ailes_home_page'))
            else:
                flash('Username and Password are not match! Please try again', category='danger')
        else:
            attempted_user = User_Account.query.filter_by(username = login_form.username_or_email.data).first()

            if attempted_user and attempted_user.check_password_correction(
                attempted_password = login_form.password.data):
                
                login_user(attempted_user)
                flash(f'You are logged in as {attempted_user.username}', 
                    category='success')
                
                return redirect(url_for('ailes_home_page'))  
            else:
                flash('Username and Password are not match! Please try again', category='danger')

    return render_template('login.html', login_form = login_form)


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():

    logout_user()

    flash(f'You have been logged out!', category='info')
    
    return redirect(url_for('home_page'))


@app.route('/ailes home')
@app.route('/ailes home/page/<int:page>/<string:sorting>', methods=['GET', 'POST'])
@login_required
def ailes_home_page(page=1, sorting = 'prority'):

    priority_sort = sorting

    try:
        ROWS_PER_PAGE = 5

        if sorting == 'added_time':
            all_drinks = User_Cooldrink.query.filter_by(
                    user_id = current_user.id
                ).order_by(User_Cooldrink.added_on.desc()).paginate(page, per_page = ROWS_PER_PAGE)
        else:
            all_drinks = User_Cooldrink.query.filter_by(
                    user_id = current_user.id
                ).order_by(User_Cooldrink.priority.desc()).paginate(page, per_page = ROWS_PER_PAGE)
        
    except OperationalError:
        flash('no cooldrinks in the users list')
        all_drinks = None

    return render_template('ailes_home.html', all_drinks = all_drinks, priority_sort = priority_sort, 
        current_datetime = datetime.utcnow())
        

@app.route('/ailes home/update drinks', methods=['GET', 'POST'])
@app.route('/ailes home/update drinks/page/<int:page>', methods=['GET', 'POST'])
@login_required
def update_drinks_page(page=1):

    edit_value_form = edit_values_form()
    remove_drink_form = remove_drinks_form()

    try:
        ROWS_PER_PAGE = 5

        all_drinks = User_Cooldrink.query.filter_by(
            user_id = current_user.id
        ).order_by(User_Cooldrink.id.desc()).paginate(page, per_page = ROWS_PER_PAGE)

    except OperationalError:
        flash('no cooldrinks in the users list')
        all_drinks = None

    if request.method == 'POST':
        if edit_value_form.validate_on_submit:
            try :
                drink_id_to_edit = int(request.form.get('drink_to_edit'))
                return redirect(url_for('edit_drinks_page', drink_id_to_edit = drink_id_to_edit))
            except Exception as e:
                flash(f'editing action has been stopped for a while, until removal action completes', category='danger') 
        
        if remove_drink_form.validate_on_submit:
            try:
                drink_id_to_remove = int(request.form.get('drink_to_remove'))

                print(drink_id_to_remove)
                drink_to_remove = User_Cooldrink.query.filter_by(
                                    id = drink_id_to_remove,
                                    user_id = current_user.id
                                    ).first()
                if drink_to_remove:
                    db.session.delete(drink_to_remove)
                    db.session.commit()

                    flash(f'the {drink_to_remove.drink_name} drink has been removed form list', category='success')
                    return redirect(url_for('update_drinks_page'))
                else:
                    flash(f'drink may not be available in the user dirnks list', category='danger')
            except Exception as e:
                flash(f'removing drinks action has been stopped for a while, until editing action completes', category='danger')

    return render_template('update_drinks.html', all_drinks = all_drinks, edit_value_form = edit_value_form,  
        remove_drink_form = remove_drink_form)


@app.route('/ailes home/update drinks/edit drink/<int:drink_id_to_edit>', methods=['GET', 'POST'])
@login_required
def edit_drinks_page(drink_id_to_edit):
    
    update_drink_form = update_drinks_form()

    drink_to_edit = User_Cooldrink.query.filter_by(
                                user_id = current_user.id,
                                id = drink_id_to_edit
                                ).first()

    editing_drink_name = drink_to_edit.drink_name

    if request.method == 'POST':
        if update_drink_form.validate_on_submit:

            if drink_to_edit:
                values_count_to_change = 4

                updated_drink_values = {'drink_name':update_drink_form.drink_name.data,
                                        'description':update_drink_form.description.data,
                                        'priority':update_drink_form.priority.data,
                                        'category':update_drink_form.category.data
                                        }

                for drink_value in updated_drink_values:
                    if drink_value == 'priority':
                        if update_drink_form.priority.data > 0:
                            User_Cooldrink.query.filter_by(
                                user_id = current_user.id,
                                id = drink_to_edit.id
                            ).update({drink_value:update_drink_form.priority.data})

                            values_count_to_change -= 1
                        continue

                    if updated_drink_values[drink_value] != '':
                        User_Cooldrink.query.filter_by(
                                user_id = current_user.id,
                                id = drink_to_edit.id
                            ).update({drink_value:updated_drink_values[drink_value]})

                        values_count_to_change -= 1
                
                drink_to_edit.last_updated = datetime.utcnow()

                db.session.commit()
                
                if values_count_to_change < 4:
                    flash(f'{drink_to_edit.drink_name} drink has been updated with new properties', category='success')
                else:
                    flash(f'{drink_to_edit.drink_name} values stayed as existed', category='info')
                return redirect(url_for('update_drinks_page'))
                
            if update_drink_form.errors != {}:
                    for error in update_drink_form.errors.values():
                        flash(f'{error[0]}', category='danger')
              
    return render_template('edit_drinks.html', editing_drink_name=editing_drink_name.lower(),
        update_drink_form = update_drink_form)


@app.route('/ailes home/add_drinks', methods=['GET', 'POST'])
@login_required
def add_drinks_page():

    add_drink_form = add_drinks_form()

    if request.method == 'POST':
        if add_drink_form.validate_on_submit():
            try:
                drink_to_add = User_Cooldrink(drink_name = add_drink_form.drink_name.data,
                                                description = add_drink_form.description.data,
                                                priority = add_drink_form.priority.data,
                                                category = add_drink_form.category.data,
                                                user_id = current_user.id,
                                                added_on = datetime.utcnow(),
                                                last_updated = datetime.utcnow()
                )
                db.session.add(drink_to_add)
                db.session.commit()
                
                flash(f'{drink_to_add.drink_name} drink added to aile', category='success')
                return redirect(url_for('add_drinks_page'))
          
            except Exception as e:
                flash(f'drink has some technical issues to add : {e}', category='danger')

        if add_drink_form.errors != {}:
                for error in add_drink_form.errors.values():
                    flash(f'{error[0]}', category='danger')

    return render_template('add_drinks.html', add_drink_form = add_drink_form)



