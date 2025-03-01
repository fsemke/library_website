from extension import db

class Book(db.Model):
    __tablename__ ='book'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, nullable=False)
    author = db.Column(db.String(128), nullable=False)
    published_date = db.Column(db.Date, nullable=False)
    img_url = db.Column(db.String(128), nullable=True)
    description = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.String(128), nullable=True)
    borrowed_from = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    borrowed_date = db.Column(db.Date, nullable=True)
    user = db.relationship('User', back_populates='books')

    def __repr__(self):
        return f'<Book {self.title}>'