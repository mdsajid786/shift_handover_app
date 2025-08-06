from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Incident, TeamMember, ShiftRoster, ShiftKeyPoint
from app import db
import plotly.graph_objs as go
import plotly
import json
from datetime import datetime, timedelta, time as dt_time
import pytz

dashboard_bp = Blueprint('dashboard', __name__)

def get_ist_now():
    utc_now = datetime.utcnow()
    ist = pytz.timezone('Asia/Kolkata')
    return utc_now.replace(tzinfo=pytz.utc).astimezone(ist)

def get_shift_type_and_next(now):
    # Shift timings (IST):
    # Morning: 6:30-15:30, Evening: 14:45-23:45, Night: 21:45-6:45 (next day)
    t = now.time()
    if dt_time(6,30) <= t < dt_time(15,30):
        return 'Morning', 'Evening'
    elif dt_time(14,45) <= t < dt_time(23,45):
        return 'Evening', 'Night'
    else:
        # Night shift covers 21:45-6:45 (next day)
        return 'Night', 'Morning'

def get_engineers_for_shift(date, shift_code):
    # shift_code: 'E' (Evening), 'D' (Day/Morning), 'N' (Night)
    entries = ShiftRoster.query.filter_by(date=date, shift_code=shift_code).all()
    member_ids = [e.team_member_id for e in entries]
    return TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []

@dashboard_bp.route('/')
@login_required
def dashboard():
    open_incidents = Incident.query.filter_by(status='Active').all()
    open_key_points = ShiftKeyPoint.query.filter_by(status='Open').all()
    ist_now = get_ist_now()
    today = ist_now.date()
    shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
    current_shift_type, next_shift_type = get_shift_type_and_next(ist_now)
    current_shift_code = shift_map[current_shift_type]
    next_shift_code = shift_map[next_shift_type]
    # For night shift, if after midnight, use previous day's date for roster
    if current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
        night_date = today - timedelta(days=1)
        current_engineers = get_engineers_for_shift(night_date, current_shift_code)
    else:
        current_engineers = get_engineers_for_shift(today, current_shift_code)
    # Next shift engineers
    if next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
        next_date = today + timedelta(days=1)
        next_engineers = get_engineers_for_shift(next_date, next_shift_code)
    else:
        next_engineers = get_engineers_for_shift(today, next_shift_code)
    # Chart.js/Plotly example
    incident_counts = [len(open_incidents), len(current_engineers), len(next_engineers)]
    labels = ['Open Incidents', 'Current Engineers', 'Next Engineers']
    bar = go.Bar(x=labels, y=incident_counts)
    data = [bar]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', open_incidents=open_incidents, current_engineers=current_engineers, next_engineers=next_engineers, graphJSON=graphJSON, open_key_points=open_key_points)
