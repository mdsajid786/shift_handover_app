
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import TeamMember, Shift, Incident, ShiftKeyPoint, current_shift_engineers, next_shift_engineers
from app import db
from services.email_service import send_handover_email

handover_bp = Blueprint('handover', __name__)

@handover_bp.route('/handover', methods=['GET', 'POST'])
@login_required
def handover():
    team_members = TeamMember.query.all()
    if request.method == 'POST':
        date = request.form['date']
        current_shift_type = request.form['current_shift_type']
        next_shift_type = request.form['next_shift_type']
        current_engineers = request.form.getlist('current_engineers')
        next_engineers = request.form.getlist('next_engineers')
        incidents = request.form.getlist('incidents')
        key_points = request.form.getlist('key_points')
        shift = Shift(date=date, current_shift_type=current_shift_type, next_shift_type=next_shift_type)
        db.session.add(shift)
        db.session.commit()
        # Add engineers to association tables
        for eng_id in current_engineers:
            member = TeamMember.query.get(int(eng_id))
            if member:
                shift.current_engineers.append(member)
        for eng_id in next_engineers:
            member = TeamMember.query.get(int(eng_id))
            if member:
                shift.next_engineers.append(member)
        db.session.commit()
        # Email notification
        send_handover_email(shift)
        flash('Handover submitted and email sent!')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('handover_form.html', team_members=team_members)
