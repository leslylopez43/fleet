from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(80), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_contact = db.Column(db.String(120), nullable=False)
    hire_start = db.Column(db.Date, nullable=False)
    hire_end = db.Column(db.Date, nullable=False)
