from flask_login import UserMixin
from extension import db

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