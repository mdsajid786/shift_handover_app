from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import TeamMember, ShiftRoster
from app import db
import pandas as pd
from werkzeug.utils import secure_filename
import os
from datetime import datetime

roster_bp = Blueprint('roster', __name__)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

@roster_bp.route('/roster', methods=['GET', 'POST'])
@login_required
def roster():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            df = pd.read_excel(filepath, header=None)
            os.remove(filepath)
            # First row: dates, first col: team member names
            dates = [df.iloc[0, j] for j in range(1, df.shape[1])]
            for i in range(1, df.shape[0]):
                member_name = df.iloc[i, 0]
                member = TeamMember.query.filter_by(name=member_name).first()
                if not member:
                    member = TeamMember(name=member_name, email='', contact_number='', role='')
                    db.session.add(member)
                    db.session.commit()
                for j, date_val in enumerate(dates):
                    shift_code = str(df.iloc[i, j+1]) if pd.notnull(df.iloc[i, j+1]) else ''
                    if date_val:
                        try:
                            date_obj = pd.to_datetime(date_val).date()
                        except Exception:
                            continue
                        roster_entry = ShiftRoster(date=date_obj, team_member_id=member.id, shift_code=shift_code)
                        db.session.add(roster_entry)
            db.session.commit()
            flash('Roster uploaded and saved!')
            return redirect(url_for('roster.roster'))
    # Display the roster table
    all_dates = db.session.query(ShiftRoster.date).distinct().order_by(ShiftRoster.date).all()
    all_members = TeamMember.query.all()
    roster_data = {}
    for member in all_members:
        roster_data[member.name] = {}
        for date_tuple in all_dates:
            date = date_tuple[0]
            entry = ShiftRoster.query.filter_by(date=date, team_member_id=member.id).first()
            roster_data[member.name][date] = entry.shift_code if entry else ''
    return render_template('shift_roster.html', all_dates=[d[0] for d in all_dates], all_members=all_members, roster_data=roster_data)
