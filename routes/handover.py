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
        shift = Shift(date=date, current_shift_type=current_shift_type, next_shift_type=next_shift_type)
        db.session.add(shift)
        db.session.commit()
        for eng_id in current_engineers:
            member = TeamMember.query.get(int(eng_id))
            if member:
                shift.current_engineers.append(member)
        for eng_id in next_engineers:
            member = TeamMember.query.get(int(eng_id))
            if member:
                shift.next_engineers.append(member)
        db.session.commit()
        # Incidents
        def add_incident(field, inc_type):
            vals = request.form.getlist(field)
            for val in vals:
                if val.strip():
                    incident = Incident(title=val, status=inc_type if inc_type in ['Active','Closed'] else '', priority='High' if inc_type=='Priority' else '', handover=val if inc_type=='Handover' else '', shift_id=shift.id, type=inc_type)
                    db.session.add(incident)
        add_incident('active_incidents', 'Active')
        add_incident('closed_incidents', 'Closed')
        add_incident('priority_incidents', 'Priority')
        add_incident('handover_incidents', 'Handover')
        db.session.commit()
        send_handover_email(shift)
        flash('Handover submitted and email sent!')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('handover_form.html', team_members=team_members)
