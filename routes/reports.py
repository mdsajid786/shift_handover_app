from flask import Blueprint, render_template, request
from flask_login import login_required
from models.models import Shift, Incident
from app import db
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/handover-reports', methods=['GET'])
@login_required
def handover_reports():
    date_filter = request.args.get('date')
    shift_type_filter = request.args.get('shift_type')
    query = Shift.query
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=date_obj)
        except Exception:
            pass
    if shift_type_filter:
        query = query.filter_by(current_shift_type=shift_type_filter)
    shifts = query.order_by(Shift.date.desc()).all()
    shift_data = []
    for shift in shifts:
        incidents = Incident.query.filter_by(shift_id=shift.id).all()
        shift_data.append({
            'shift': shift,
            'incidents': incidents
        })
    return render_template('handover_reports.html', shift_data=shift_data, date_filter=date_filter or '', shift_type_filter=shift_type_filter or '')
