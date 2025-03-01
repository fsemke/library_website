from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os

from models import Book, History, User
from extension import db

# Doppelt, später schöner machen
UPLOAD_FOLDER = 'static/uploads/'
DB_FOLDER = 'instance/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

library_bp = Blueprint('library', __name__)

@library_bp.route('/library')
@login_required
def library():
    available = Book.query.filter(Book.borrowed_from == None).all()
    not_available = Book.query.filter(Book.borrowed_from != None).all()

    return render_template('library.html', available=available, not_available=not_available, loggedIn = True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

@library_bp.route('/addbook', methods=['GET','POST'])
@login_required
def addBook():
    if not current_user.admin:
        return redirect(url_for('library.library'))
    if request.method == 'POST':
        # Create new book
        file = request.files['image']
        title = request.form['title']
        author = request.form['author']
        descrip = request.form['description']
        print(f"Description: {descrip}")


        publishedDate = request.form['published_date']
        publishedDate = datetime.strptime(publishedDate, '%Y-%m-%d')

        try:
            new_book = Book(
                title=title,
                author=author,
                published_date=publishedDate,
                description=descrip,
                img_url="",
                admin_notes="")
            db.session.add(new_book)
            db.session.commit()

            new_book = db.session.get(Book, new_book.id)
            if file.filename == '':
                return redirect(url_for('library.addBook'))
            upload_path = ''
            if file and allowed_file(file.filename):
                filename = secure_filename(title)
                upload_path = os.path.join(UPLOAD_FOLDER, filename + '.' + get_extension(file.filename))
                file.save(upload_path)
            else:
                return redirect(url_for('library.addBook'))
            new_book.img_url = os.path.join('/', upload_path)
            db.session.commit()
        except Exception as e:
            print(f"Error while adding the book: {e}")
            flash("Can't save the book, is the title unique?")
            return redirect(url_for('library.addBook'))

        return redirect(url_for('library.library'))
    
    else:
        return render_template('add_book.html', loggedIn = True)
    
@library_bp.route('/editbook/<int:book_id>', methods=['GET','POST'])
@login_required
def editBook(book_id):
    if request.method == 'POST':
        if not current_user.admin:
            return redirect(url_for('library.book_detail', book_id=book_id))
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
        book.description = request.form['description']
        publishedDate = request.form['published_date']
        book.published_date = datetime.strptime(publishedDate, '%Y-%m-%d')
        file = request.files['image']
        if file and allowed_file(file.filename) and file.filename != '':
            filename = secure_filename(book.title)
            upload_path = os.path.join(UPLOAD_FOLDER, filename + '.' + get_extension(file.filename))
            file.save(upload_path)
            book.img_url = os.path.join('/', upload_path)
        db.session.commit()
        return redirect(url_for('library.book_detail', book_id=book_id))

    book = Book.query.get(book_id)
    return render_template('edit_book.html', book = book, loggedIn = True)


@library_bp.route('/book/<int:book_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('library.book_detail', book_id=book.id))

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

@library_bp.route('/book/<int:book_id>/note', methods=['POST'])
@login_required
def save_note(book_id):
    if not current_user.admin:
        return redirect(url_for('library.book_detail', book_id=book_id))
    book = Book.query.get_or_404(book_id)
    book.admin_notes = request.form['textarea']
    db.session.commit()
    return redirect(url_for('library.book_detail', book_id=book_id))

@library_bp.route('/bookreturn/<int:book_id>', methods=['POST'])
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
    return redirect(url_for('library.book_detail', book_id=book.id))

@library_bp.route('/deletebook/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.admin:
        print('Not an admin')
        return redirect(url_for('library.library'))

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
    return redirect(url_for('library.library'))