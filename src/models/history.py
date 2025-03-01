from extension import db

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(128), nullable=False)
    date = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship("User")
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    book = db.relationship("Book")