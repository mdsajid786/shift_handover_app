from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Engineer, Shift, Incident, ShiftKeyPoint
from app import db
from services.email_service import send_handover_email

handover_bp = Blueprint('handover', __name__)

@handover_bp.route('/handover', methods=['GET', 'POST'])
@login_required
def handover():
    engineers = Engineer.query.all()
    if request.method == 'POST':
        # Collect form data
        date = request.form['date']
        current_engineers = request.form.getlist('current_engineers')
        next_engineers = request.form.getlist('next_engineers')
        incidents = request.form.getlist('incidents')
        key_points = request.form.getlist('key_points')
        # Save to DB (simplified)
        shift = Shift(date=date)
        db.session.add(shift)
        db.session.commit()
        # Email notification
        send_handover_email(shift)
        flash('Handover submitted and email sent!')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('handover_form.html', engineers=engineers)
