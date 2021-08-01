from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import logging
from logging import Formatter, FileHandler

app = Flask(__name__)

file_handler = FileHandler('logging.log')
handler = logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():

    #new_user = User(username="nhoriza", password="password", givingPoints=0, contactNum="09123456789")
    #new_user =User(username="cindy", password="pass", givingPoints=0, contactNum="09987654321")
    #new_user =User(username="icaro", password="123qwe", givingPoints=0, contactNum="09166263822")
    # db.session.add(new_user)
    # db.session.commit()

    if request.method == 'POST':
        data = request.form
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        try:
            if user:
                if password == user.password:
                    login_user(user, remember=True)
                    return redirect(url_for('views.landing'))
                else:
                    flash('Incorrect Username/Password', category='error')
                    raise ValueError('The username and password does not match')
            
            else:
                flash('Incorrect Username/Password', category='error')
                raise ValueError('User is not registered')

        except ValueError as err: 
            app.logger.error(err)

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))