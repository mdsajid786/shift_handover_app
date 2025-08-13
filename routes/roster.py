from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import TeamMember, ShiftRoster
from app import db
from datetime import datetime

roster_bp = Blueprint('roster', __name__)



# Shift Roster View with Month/Year filters
@roster_bp.route('/roster', methods=['GET', 'POST'])
@login_required
def roster():
    if request.method == 'POST' and current_user.role == 'viewer':
        flash('You do not have permission to edit shift roster.')
        return redirect(url_for('roster.roster'))
    # Get filter values from query params
    import calendar
    month_str = request.args.get('month')
    year = request.args.get('year', default=None, type=int)
    now = datetime.now()
    month = None
    if month_str:
        try:
            month = list(calendar.month_name).index(month_str)
        except ValueError:
            month = None
    if not month:
        month = now.month
    if not year:
        year = now.year
    filter_date = request.args.get('filter_date')
    filter_shift = request.args.get('filter_shift')
    query = db.session.query(ShiftRoster)
    if current_user.role != 'admin':
        query = query.filter(ShiftRoster.account_id==current_user.account_id, ShiftRoster.team_id==current_user.team_id)
    if month:
        query = query.filter(db.extract('month', ShiftRoster.date) == month)
    if year:
        query = query.filter(db.extract('year', ShiftRoster.date) == year)
    roster_entries = query.order_by(ShiftRoster.date).all()
    tm_query = TeamMember.query
    if current_user.role != 'admin':
        tm_query = tm_query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id)
    all_members = tm_query.all()
    # Build a set of all dates in the filtered result
    all_dates = sorted({entry.date for entry in roster_entries})
    # Build roster data: {member_name: {date: shift_code}}
    roster_data = {member.name: {date: '' for date in all_dates} for member in all_members}
    for entry in roster_entries:
        member = next((m for m in all_members if m.id == entry.team_member_id), None)
        if member:
            roster_data[member.name][entry.date] = entry.shift_code
    # For dropdowns
    months = [calendar.month_name[i] for i in range(1, 13)]
    years = sorted({d.date.year for d in db.session.query(ShiftRoster.date).distinct() if d.date})

    # Additional filter: present team members for selected date and shift
    present_members = []
    present_members_by_shift = {}
    if filter_date:
        date_obj = datetime.strptime(filter_date, '%Y-%m-%d').date()
        if filter_shift is not None and filter_shift != '':
            present_entries = ShiftRoster.query.filter(ShiftRoster.date == date_obj, ShiftRoster.shift_code == filter_shift).all()
            present_member_ids = [e.team_member_id for e in present_entries]
            present_members = TeamMember.query.filter(TeamMember.id.in_(present_member_ids)).all() if present_member_ids else []
        else:
            # Group by shift_code, including LE (Late Evening) and G (General)
            shift_codes = ['D', 'E', 'N', 'LE', 'G']
            for code in shift_codes:
                entries = ShiftRoster.query.filter(ShiftRoster.date == date_obj, ShiftRoster.shift_code == code).all()
                member_ids = [e.team_member_id for e in entries]
                members = TeamMember.query.filter(TeamMember.id.in_(member_ids)).all() if member_ids else []
                present_members_by_shift[code] = members
            # Ensure all shift codes are present in the dict, even if empty
            for code in shift_codes:
                if code not in present_members_by_shift:
                    present_members_by_shift[code] = []

    return render_template(
        'shift_roster.html',
        all_dates=all_dates,
        all_members=all_members,
        roster_data=roster_data,
        months=months,
        years=years,
        selected_month=month,
        selected_year=year,
        filter_date=filter_date,
        filter_shift=filter_shift,
        present_members=present_members,
        present_members_by_shift=present_members_by_shift if 'present_members_by_shift' in locals() else {}
    )
