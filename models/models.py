
from app import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class ShiftRoster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    shift_code = db.Column(db.String(8), nullable=True)  # E, D, N, G, LE, VL, HL, CO, or blank

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contact_number = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(64))

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    current_shift_type = db.Column(db.String(16), nullable=False) # Morning/Evening/Night
    next_shift_type = db.Column(db.String(16), nullable=False)
    current_engineers = db.relationship('TeamMember', secondary='current_shift_engineers')
    next_engineers = db.relationship('TeamMember', secondary='next_shift_engineers')

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(16), nullable=False) # Active/Closed
    priority = db.Column(db.String(16), nullable=False)
    handover = db.Column(db.Text)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    type = db.Column(db.String(32), nullable=False) # Active, Closed, Priority, Handover

class ShiftKeyPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), nullable=False) # Open/Closed
    responsible_engineer_id = db.Column(db.Integer, db.ForeignKey('team_member.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))

# Association tables
current_shift_engineers = db.Table('current_shift_engineers',
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.id')),
    db.Column('team_member_id', db.Integer, db.ForeignKey('team_member.id'))
)

next_shift_engineers = db.Table('next_shift_engineers',
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.id')),
    db.Column('team_member_id', db.Integer, db.ForeignKey('team_member.id'))
)
