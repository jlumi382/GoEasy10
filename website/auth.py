from flask import Blueprint, request, url_for, redirect, flash, render_template
from . import models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from . import db
from .utils import email_regex, phone_regex
from re import match

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = models.User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=False)
                return redirect(url_for('admin.admin_home'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('Incorrect username.', category='error')

        return redirect(url_for('admin.admin_home'))
    return render_template('login.html', user=current_user)
    

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone = request.form.get('phone') if not request.form.get('phone').startswith('0') else request.form.get('phone')[1:]
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = models.User.query.filter_by(username=username).first()

        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 1 character.', category='error')
        elif len(phone) != 10:
            flash('Phone number must be 10 digits. Example: 9632196204.', category='error')
        elif not match(phone_regex, phone):
            flash('Invalid phone number format. Example: 9632196204.', category='error')
        elif not match(email_regex, email):
            flash('Invalid email.', category='error')
        else:
            new_user = models.User(username=username, first_name=first_name, surname=surname, password=generate_password_hash(password1), email=email, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=False)
            flash('Account created!', category='success')
            return redirect(url_for('admin.admin_home'))

    return render_template("sign_up.html", user=current_user)
