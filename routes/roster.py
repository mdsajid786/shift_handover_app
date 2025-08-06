from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Engineer, Shift
from app import db

roster_bp = Blueprint('roster', __name__)

@roster_bp.route('/roster')
@login_required
def roster():
    shifts = Shift.query.order_by(Shift.date.desc()).all()
    engineers = Engineer.query.all()
    # Basic calendar view (table)
    return render_template('shift_roster.html', shifts=shifts, engineers=engineers)
