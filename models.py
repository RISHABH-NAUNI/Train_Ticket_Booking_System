from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_vip = db.Column(db.Boolean, default=False)  #  NEW FIELD
    email = db.Column(db.String(120), unique=True, nullable=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Train(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(10), nullable=False)
    arrival_time = db.Column(db.String(10), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='train', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    train_id = db.Column(db.String(10), db.ForeignKey('train.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
