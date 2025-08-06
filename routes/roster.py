from flask import Blueprint, render_template, request
from flask_login import login_required
from models.models import TeamMember, ShiftRoster
from app import db
from datetime import datetime

roster_bp = Blueprint('roster', __name__)



# Shift Roster View with Month/Year filters
@roster_bp.route('/roster', methods=['GET'])
@login_required
def roster():
    # Get filter values from query params
    month = request.args.get('month', default=None, type=int)
    year = request.args.get('year', default=None, type=int)
    query = db.session.query(ShiftRoster)
    if month:
        query = query.filter(db.extract('month', ShiftRoster.date) == month)
    if year:
        query = query.filter(db.extract('year', ShiftRoster.date) == year)
    roster_entries = query.order_by(ShiftRoster.date).all()
    all_members = TeamMember.query.all()
    # Build a set of all dates in the filtered result
    all_dates = sorted({entry.date for entry in roster_entries})
    # Build roster data: {member_name: {date: shift_code}}
    roster_data = {member.name: {date: '' for date in all_dates} for member in all_members}
    for entry in roster_entries:
        member = next((m for m in all_members if m.id == entry.team_member_id), None)
        if member:
            roster_data[member.name][entry.date] = entry.shift_code
    # For dropdowns
    import calendar
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = sorted({d.date.year for d in db.session.query(ShiftRoster.date).distinct() if d.date})
    return render_template('shift_roster.html', all_dates=all_dates, all_members=all_members, roster_data=roster_data, months=months, years=years, selected_month=month, selected_year=year)
