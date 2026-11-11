import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, send_from_directory, url_for
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required

from config import BASE_DIR, DB_DIRECTORY, UPLOAD_DIRECTORY
from extension import bcrypt, db
from models import Book, User
from routes import auth_bp, library_bp, user_bp

load_dotenv(dotenv_path=BASE_DIR / '.env')

UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
DB_DIRECTORY.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "src" /"static"),
    template_folder=str(BASE_DIR / "src" / "templates")
)
CORS(app)

db_uri = os.getenv('DATABASE_URI')
if db_uri and db_uri.startswith('sqlite:///'):
    db_file = db_uri.replace('sqlite:///', '')
    db_path = DB_DIRECTORY / db_file
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

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

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_DIRECTORY), filename)

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

    debug_mode = len(sys.argv) > 1 and sys.argv[1].lower() == 'debug'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
