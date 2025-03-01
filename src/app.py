from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, login_required, current_user
from datetime import datetime
from flask_cors import CORS
from dotenv import load_dotenv
import os

from extension import db, bcrypt
from models import User, Book
from routes import auth_bp, library_bp, user_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads/'
DB_FOLDER = 'instance/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True

db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(library_bp)
app.register_blueprint(user_bp)

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('library.library'))
    else:
        return render_template('home_logged_out.html', loggedIn = False)

@app.route('/statistics')
@login_required
def statistic():
    if current_user.admin:

        books = db.session.query(Book)\
        .where(Book.borrowed_from != None)\
        .join(User, Book.borrowed_from == User.id)\
        .order_by(Book.borrowed_date.asc())\
        .all()

        for book in books:
            book.borrowed_days = (datetime.now().date() - book.borrowed_date).days

        return render_template('statistics.html', books=books, loggedIn=True)
    return redirect(url_for('library'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    os.makedirs(os.path.dirname(UPLOAD_FOLDER), exist_ok=True)
    os.makedirs(os.path.dirname(DB_FOLDER), exist_ok=True)
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)