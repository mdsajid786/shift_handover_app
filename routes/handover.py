
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import TeamMember, Shift, Incident, ShiftKeyPoint, ShiftRoster, current_shift_engineers, next_shift_engineers
from app import db
from services.email_service import send_handover_email
from datetime import datetime, timedelta, time as dt_time
import pytz

handover_bp = Blueprint('handover', __name__)


@handover_bp.route('/handover', methods=['GET', 'POST'])
@login_required
def handover():
    team_members = TeamMember.query.all()

    def get_ist_now():
        utc_now = datetime.utcnow()
        ist = pytz.timezone('Asia/Kolkata')
        return utc_now.replace(tzinfo=pytz.utc).astimezone(ist)

    def get_shift_type_and_next(now):
        t = now.time()
        if dt_time(6,30) <= t < dt_time(15,30):
            return 'Morning', 'Evening'
        elif dt_time(14,45) <= t < dt_time(23,45):
            return 'Evening', 'Night'
        else:
            return 'Night', 'Morning'

    def get_engineers_for_shift(date, shift_code):
        entries = ShiftRoster.query.filter_by(date=date, shift_code=shift_code).all()
        member_ids = [e.team_member_id for e in entries]
        return TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []

    # Default: use current IST time for GET, or use form date/shifts for POST
    if request.method == 'POST':
        date_str = request.form['date']
        current_shift_type = request.form['current_shift_type']
        next_shift_type = request.form['next_shift_type']
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
        current_shift_code = shift_map[current_shift_type]
        next_shift_code = shift_map[next_shift_type]
        # For night shift, if before 6:45, use previous day for current shift
        ist_now = get_ist_now()
        if current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
            night_date = date - timedelta(days=1)
            current_engineers_objs = get_engineers_for_shift(night_date, current_shift_code)
        else:
            current_engineers_objs = get_engineers_for_shift(date, current_shift_code)
        if next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
            next_date = date + timedelta(days=1)
            next_engineers_objs = get_engineers_for_shift(next_date, next_shift_code)
        else:
            next_engineers_objs = get_engineers_for_shift(date, next_shift_code)
        # Save shift
        shift = Shift(date=date, current_shift_type=current_shift_type, next_shift_type=next_shift_type)
        db.session.add(shift)
        db.session.commit()
        for member in current_engineers_objs:
            shift.current_engineers.append(member)
        for member in next_engineers_objs:
            shift.next_engineers.append(member)
        db.session.commit()
        # Incidents
        def add_incident(field, inc_type):
            vals = request.form.getlist(field)
            for val in vals:
                if val.strip():
                    incident = Incident(title=val, status=inc_type if inc_type in ['Active','Closed'] else '', priority='High' if inc_type=='Priority' else '', handover=val if inc_type=='Handover' else '', shift_id=shift.id, type=inc_type)
                    db.session.add(incident)
        add_incident('open_incidents', 'Active')
        add_incident('closed_incidents', 'Closed')
        add_incident('priority_incidents', 'Priority')
        add_incident('handover_incidents', 'Handover')

        # Key Points
        key_point_numbers = request.form.getlist('key_point_number')
        key_point_details = request.form.getlist('key_point_details')
        responsible_persons = request.form.getlist('responsible_person')
        key_point_statuses = request.form.getlist('key_point_status')
        for i in range(len(key_point_numbers)):
            details = key_point_details[i].strip() if i < len(key_point_details) else ''
            responsible_id = responsible_persons[i] if i < len(responsible_persons) else ''
            status = key_point_statuses[i] if i < len(key_point_statuses) else 'Open'
            if details:
                kp = ShiftKeyPoint(
                    description=details,
                    status=status,
                    responsible_engineer_id=int(responsible_id) if responsible_id else None,
                    shift_id=shift.id
                )
                db.session.add(kp)
        db.session.commit()
        send_handover_email(shift)
        flash('Handover submitted and email sent!')
        return redirect(url_for('dashboard.dashboard'))
    else:
        # GET: auto-populate engineers using dashboard logic
        ist_now = get_ist_now()
        today = ist_now.date()
        shift_map = {'Morning': 'D', 'Evening': 'E', 'Night': 'N'}
        current_shift_type, next_shift_type = get_shift_type_and_next(ist_now)
        current_shift_code = shift_map[current_shift_type]
        next_shift_code = shift_map[next_shift_type]
        if current_shift_type == 'Night' and ist_now.time() < dt_time(6,45):
            night_date = today - timedelta(days=1)
            current_engineers_objs = get_engineers_for_shift(night_date, current_shift_code)
        else:
            current_engineers_objs = get_engineers_for_shift(today, current_shift_code)
        if next_shift_type == 'Night' and ist_now.time() >= dt_time(21,45):
            next_date = today + timedelta(days=1)
            next_engineers_objs = get_engineers_for_shift(next_date, next_shift_code)
        else:
            next_engineers_objs = get_engineers_for_shift(today, next_shift_code)
        current_engineers = [m.name for m in current_engineers_objs]
        next_engineers = [m.name for m in next_engineers_objs]
        # Fetch all open key points to carry forward
        open_key_points = ShiftKeyPoint.query.filter_by(status='Open').all()
        return render_template(
            'handover_form.html',
            team_members=team_members,
            current_engineers=current_engineers,
            next_engineers=next_engineers,
            current_shift_type=current_shift_type,
            next_shift_type=next_shift_type,
            open_key_points=open_key_points
        )
