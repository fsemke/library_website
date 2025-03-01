from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user

from models import User
from extension import db, bcrypt

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    # Delete User
    if request.method == 'POST':
        if not current_user.admin:
            print('Not an admin')
            return redirect(url_for('user.users'))

        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user and user.admin == False:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('user.users'))

    unsorted_users = User.query.all()
    users = sorted(unsorted_users, key=lambda user: user.firstname.casefold())
    return render_template('users.html', users=users, loggedIn=True)

@user_bp.route('/upgrade', methods=['POST'])
@login_required
def userToAdmin():
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('user.users'))

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if user and user.admin == False:
        user.admin = True
        db.session.commit()
    return redirect(url_for('user.user', user_id=user_id))

@user_bp.route('/downgrade', methods=['POST'])
@login_required
def adminToUser():
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('user.users'))

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if user and user.admin == True:
        user.admin = False
        db.session.commit()
    return redirect(url_for('user.user', user_id=user_id))

@user_bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user, loggedIn=True)

@user_bp.route('/pwreset', methods=['POST'])
@login_required
def pwreset():
    user_id = int(request.form.get('user_id'))
    if current_user.admin or current_user.id == user_id:
        newPw = request.form.get('newPw')
        user = User.query.get_or_404(user_id)
        user.password = bcrypt.generate_password_hash(newPw).decode('utf-8')
        db.session.commit()
    else:
        print('Not an admin')
    return redirect(url_for('user.users'))