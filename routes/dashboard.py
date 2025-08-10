from flask import Blueprint, render_template, request
from flask_login import login_required
from models.models import Incident, TeamMember, ShiftRoster, ShiftKeyPoint, Shift
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
    # Date range filter
    range_opt = request.args.get('range', '7d')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Remove single_date, only support custom range and standard options
    ist_now = get_ist_now()
    today = ist_now.date()
    if range_opt == '1d':
        from_date = today - timedelta(days=1)
        to_date = today
    elif range_opt == '7d':
        from_date = today - timedelta(days=7)
        to_date = today
    elif range_opt == '30d':
        from_date = today - timedelta(days=30)
        to_date = today
    elif range_opt == '1y':
        from_date = today - timedelta(days=365)
        to_date = today
    elif range_opt == 'custom' and start_date and end_date:
        from_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:  # default 7d
        from_date = today - timedelta(days=7)
        to_date = today

    # Summary counts for chart
    open_count = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id)
    open_count = open_count.filter(Incident.status=='Active', Incident.type=='Active', Shift.date >= from_date, Shift.date <= to_date).count()
    closed_count = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id)
    closed_count = closed_count.filter(Incident.status=='Closed', Incident.type=='Closed', Shift.date >= from_date, Shift.date <= to_date).count()
    priority_count = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id)
    priority_count = priority_count.filter(Incident.type=='Priority', Shift.date >= from_date, Shift.date <= to_date).count()

    # For widget display (current day)
    # Deduplicate open incidents by title (show only latest per title)
    inc_subq = db.session.query(
        Incident.title,
        db.func.max(Incident.id).label('max_id')
    ).filter(Incident.status=='Active', Incident.type=='Active', Shift.date==today).group_by(Incident.title).subquery()
    open_incidents = db.session.query(Incident).join(
        inc_subq, Incident.id == inc_subq.c.max_id
    ).all()

    # Deduplicate open key points by description and jira_id (show only latest per pair), only non-Closed
    kp_subq = db.session.query(
        ShiftKeyPoint.description,
        ShiftKeyPoint.jira_id,
        db.func.max(ShiftKeyPoint.id).label('max_id')
    ).filter(ShiftKeyPoint.status.in_(['Open', 'In Progress'])).group_by(ShiftKeyPoint.description, ShiftKeyPoint.jira_id).subquery()
    open_key_points = db.session.query(ShiftKeyPoint).join(
        kp_subq, ShiftKeyPoint.id == kp_subq.c.max_id
    ).filter(ShiftKeyPoint.status.in_(['Open', 'In Progress'])).all()
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

    # Date-wise chart data
    date_list = [(from_date + timedelta(days=i)) for i in range((to_date - from_date).days + 1)]
    open_counts = []
    closed_counts = []
    handover_counts = []
    priority_counts = []
    for d in date_list:
        open_c = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id) \
            .filter(Incident.status=='Active', Incident.type=='Active', Shift.date==d).count()
        closed_c = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id) \
            .filter(Incident.status=='Closed', Incident.type=='Closed', Shift.date==d).count()
        handover_c = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id) \
            .filter(Incident.type=='Handover', Shift.date==d).count()
        priority_c = db.session.query(Incident).join(Shift, Incident.shift_id == Shift.id) \
            .filter(Incident.type=='Priority', Shift.date==d).count()
        open_counts.append(open_c)
        closed_counts.append(closed_c)
        handover_counts.append(handover_c)
        priority_counts.append(priority_c)

    x_dates = [d.strftime('%Y-%m-%d') for d in date_list]
    trace_open = go.Bar(x=x_dates, y=open_counts, name='Open Incidents')
    trace_closed = go.Bar(x=x_dates, y=closed_counts, name='Closed Incidents')
    trace_handover = go.Bar(x=x_dates, y=handover_counts, name='Handover Incidents')
    trace_priority = go.Bar(x=x_dates, y=priority_counts, name='Priority Incidents')
    data = [trace_open, trace_closed, trace_handover, trace_priority]
    layout = go.Layout(barmode='group', xaxis={'title': 'Date'}, yaxis={'title': 'Count'}, title='Incidents by Date')
    graphJSON = json.dumps({'data': data, 'layout': layout}, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template(
        'dashboard.html',
        open_incidents=open_incidents,
        current_engineers=current_engineers,
        next_engineers=next_engineers,
        graphJSON=graphJSON,
        open_key_points=open_key_points,
        selected_range=range_opt,
        start_date=start_date or from_date.strftime('%Y-%m-%d'),
        end_date=end_date or to_date.strftime('%Y-%m-%d')
    )
