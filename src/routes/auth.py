from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from extension import bcrypt, db
import os

from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('library.library'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('library.library'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        registercode = request.form['registercode']
        
        if os.getenv('REGISTERCODE') != registercode:
            return redirect(url_for('auth.register'))
        
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')
        # If first User, add Admin privilege
        if User.query.count()  == 0:
            new_user = User(username=username, password=hashed_password, firstname=firstname, lastname=lastname, admin=True)
        else:
            new_user = User(username=username, password=hashed_password, firstname=firstname, lastname=lastname, admin=False)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))