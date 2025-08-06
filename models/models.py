from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Engineer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    current_engineers = db.relationship('Engineer', secondary='current_shift_engineers')
    next_engineers = db.relationship('Engineer', secondary='next_shift_engineers')

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(16), nullable=False) # Active/Closed
    priority = db.Column(db.String(16), nullable=False)
    handover = db.Column(db.Text)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))

class ShiftKeyPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False) # Open/Closed
    responsible_engineer_id = db.Column(db.Integer, db.ForeignKey('engineer.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))

# Association tables
current_shift_engineers = db.Table('current_shift_engineers',
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.id')),
    db.Column('engineer_id', db.Integer, db.ForeignKey('engineer.id'))
)

next_shift_engineers = db.Table('next_shift_engineers',
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.id')),
    db.Column('engineer_id', db.Integer, db.ForeignKey('engineer.id'))
)
