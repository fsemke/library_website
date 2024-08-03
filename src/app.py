from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads/'
DB_FOLDER = 'instance/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))




class User(db.Model, UserMixin):
    __tablename__ = 'user'
     
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    books = db.relationship('Book', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    __tablename__ ='book'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, nullable=False)
    author = db.Column(db.String(128), nullable=False)
    published_date = db.Column(db.Date, nullable=False)
    img_url = db.Column(db.String(128), nullable=True)
    admin_notes = db.Column(db.String(128), nullable=True)
    borrowed_from = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    borrowed_date = db.Column(db.Date, nullable=True)
    user = db.relationship('User', back_populates='books')

    def __repr__(self):
        return f'<Book {self.title}>'

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(128), nullable=False)
    date = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship("User")
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    book = db.relationship("Book")



@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template('home_logged_in.html', loggedIn = True)
    else:
        return render_template('home_logged_out.html', loggedIn = False)

@app.route('/library')
@login_required
def library():
    available = Book.query.filter(Book.borrowed_from == None).all()
    not_available = Book.query.filter(Book.borrowed_from != None).all()

    return render_template('library.html', available=available, not_available=not_available, loggedIn = True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

@app.route('/addbook', methods=['GET','POST'])
@login_required
def addBook():
    if not current_user.admin:
        return redirect(url_for('library'))
    if request.method == 'POST':
        # Create new book
        file = request.files['image']
        title = request.form['title']
        author = request.form['author']
        if file.filename == '':
            return redirect(url_for('addbook'))

        upload_path = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(title)
            upload_path = os.path.join(UPLOAD_FOLDER, filename + '.' + get_extension(file.filename))
            file.save(upload_path)
        else:
            redirect(url_for('addbook'))
        imgUrl = os.path.join('/', upload_path)
        publishedDate = request.form['published_date']
        publishedDate = datetime.strptime(publishedDate, '%Y-%m-%d')

        new_book = Book(
            title=title,
            author=author,
            published_date=publishedDate,
            img_url=imgUrl)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('library'))
    
    else:
        return render_template('add_book.html', loggedIn = True)
    
@app.route('/editbook/<int:book_id>', methods=['GET','POST'])
@login_required
def editBook(book_id):
    if request.method == 'POST':
        if not current_user.admin:
            return redirect(url_for('book_detail', book_id=book_id))
        book = Book.query.get(book_id)
        try:
            if book.title != request.form['title']:
                renamed_url = os.path.join(UPLOAD_FOLDER, secure_filename(request.form['title']) + '.' + get_extension(book.img_url))
                os.rename('.' + book.img_url, renamed_url)
                print(renamed_url)
                book.img_url = '/' + renamed_url
        except Exception as e:
            print(f"Can't rename the file: {e}")
        book.title = request.form['title']
        book.author = request.form['author']
        publishedDate = request.form['published_date']
        book.published_date = datetime.strptime(publishedDate, '%Y-%m-%d')
        file = request.files['image']
        if file and allowed_file(file.filename) and file.filename != '':
            filename = secure_filename(book.title)
            upload_path = os.path.join(UPLOAD_FOLDER, filename + '.' + get_extension(file.filename))
            file.save(upload_path)
            book.img_url = os.path.join('/', upload_path)
        db.session.commit()
        return redirect(url_for('book_detail', book_id=book_id))

    book = Book.query.get(book_id)
    return render_template('edit_book.html', book = book, loggedIn = True)


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_detail(book_id):
    if request.method == 'POST':
        user = User.query.get(current_user.id)

        book = Book.query.get_or_404(book_id)
        book.borrowed_from = user.id
        book.borrowed_date = datetime.now()

        new_history = History(
            action="borrow",
            date=datetime.now(),
            user_id=user.id,
            book_id=book.id
            )
        
        db.session.add(new_history)
        db.session.commit()
        return redirect(url_for('book_detail', book_id=book.id))

    book = Book.query.get_or_404(book_id)
    history = db.session.query(History)\
        .join(User, History.user_id == User.id)\
        .filter(History.book_id == book.id)\
        .order_by(
            History.date.desc(),
            History.id.desc()
        )\
        .limit(15)
    return render_template('book_detail.html', book=book, history=history, loggedIn=True)

@app.route('/book/<int:book_id>/note', methods=['POST'])
@login_required
def save_note(book_id):
    if not current_user.admin:
        return redirect(url_for('book_detail', book_id=book_id))
    book = Book.query.get_or_404(book_id)
    book.admin_notes = request.form['textarea']
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/bookreturn/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.borrowed_from == current_user.id or current_user.admin:
        book.borrowed_from = None
        book.borrowed_date = None

        new_history = History(
            action="return",
            date=datetime.now(),
            user_id=current_user.id,
            book_id=book.id
            )
        
        db.session.add(new_history)
        db.session.commit()
    return redirect(url_for('book_detail', book_id=book.id))

@app.route('/deletebook/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('library'))

    book = Book.query.get(book_id)
    try:
        os.remove(os.path.join('.' + book.img_url))
    except OSError as e:
        print(f"File '{book.title}' could not be deleted: {e}")

    try:
        db.session.delete(book)
        db.session.commit()
    except:
        print('book not deleted from database')
    return redirect(url_for('library'))

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
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('library'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('library'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
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

        return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    # Delete User
    if request.method == 'POST':
        if not current_user.admin:
            print('Not an admin')
            return redirect(url_for('users'))

        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user and user.admin == False:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('users'))

    unsorted_users = User.query.all()
    users = sorted(unsorted_users, key=lambda user: user.firstname.casefold())
    return render_template('users.html', users=users, loggedIn=True)

@app.route('/upgrade', methods=['POST'])
@login_required
def userToAdmin():
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('users'))

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if user and user.admin == False:
        user.admin = True
        db.session.commit()
    return redirect(url_for('user', user_id=user_id))

@app.route('/downgrade', methods=['POST'])
@login_required
def adminToUser():
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('users'))

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if user and user.admin == True:
        user.admin = False
        db.session.commit()
    return redirect(url_for('user', user_id=user_id))

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user, loggedIn=True)

@app.route('/pwreset', methods=['POST'])
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
    return redirect(url_for('users'))
    
        


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    os.makedirs(os.path.dirname(UPLOAD_FOLDER), exist_ok=True)
    os.makedirs(os.path.dirname(DB_FOLDER), exist_ok=True)
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)