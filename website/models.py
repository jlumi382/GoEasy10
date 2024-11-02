from . import db
from flask_login import UserMixin

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    short_name = db.Column(db.String(10), nullable=False, unique=True)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(25), nullable=False)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reflection = db.Column(db.Text, nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('events', lazy=True))
    
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizers.id'))
    organizer = db.relationship('Organizer', backref=db.backref('events', lazy=True))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

    thumbnail = db.Column(db.String(100), nullable=False)
    proof = db.Column(db.String(100), nullable=False)

class Organizer(db.Model):
    __tablename__ = 'organizers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(25), nullable=False)
    logo = db.Column(db.String(100), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    summary = db.Column(db.String(150))
