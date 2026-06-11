from extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    cars = db.relationship('Car', backref='owner', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(120), nullable=False)

    records = db.relationship('ServiceRecord', backref='car', lazy=True, cascade='all, delete-orphan')

class ServiceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    service_type = db.Column(db.String(120), nullable=False)   # e.g., Basic Wash, Premium, Ceramic
    amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, default='')
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
