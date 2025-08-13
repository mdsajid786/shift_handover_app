from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import TeamMember
from app import db

team_bp = Blueprint('team', __name__)


# List/add/edit/delete team members
@team_bp.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    if request.method == 'POST' and current_user.role == 'viewer':
        flash('You do not have permission to edit team details.')
        return redirect(url_for('team.team'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form['name']
            email = request.form['email']
            contact_number = request.form['contact_number']
            role = request.form.get('role')
            member = TeamMember(name=name, email=email, contact_number=contact_number, role=role,
                               account_id=current_user.account_id, team_id=current_user.team_id)
            db.session.add(member)
            db.session.commit()
            flash('Team member added!')
        elif action == 'edit':
            member_id = request.form['member_id']
            member = TeamMember.query.get(member_id)
            if member and (current_user.role == 'admin' or (member.account_id == current_user.account_id and member.team_id == current_user.team_id)):
                member.name = request.form['name']
                member.email = request.form['email']
                member.contact_number = request.form['contact_number']
                member.role = request.form.get('role')
                db.session.commit()
                flash('Team member updated!')
        elif action == 'delete':
            member_id = request.form['member_id']
            member = TeamMember.query.get(member_id)
            if member and (current_user.role == 'admin' or (member.account_id == current_user.account_id and member.team_id == current_user.team_id)):
                try:
                    db.session.delete(member)
                    db.session.commit()
                    flash('Team member deleted!')
                except Exception as e:
                    db.session.rollback()
                    if 'foreign key constraint fails' in str(e).lower():
                        flash('Cannot delete team member: assigned in shift roster or related records exist.', 'danger')
                    else:
                        flash(f'Error deleting team member: {e}', 'danger')
        return redirect(url_for('team.team'))
    tm_query = TeamMember.query
    if current_user.role != 'admin':
        tm_query = tm_query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id)
    members = tm_query.all()
    return render_template('team_details.html', members=members)
