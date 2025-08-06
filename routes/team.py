from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import TeamMember
from app import db

team_bp = Blueprint('team', __name__)


# List/add/edit/delete team members
@team_bp.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form['name']
            email = request.form['email']
            contact_number = request.form['contact_number']
            role = request.form.get('role')
            member = TeamMember(name=name, email=email, contact_number=contact_number, role=role)
            db.session.add(member)
            db.session.commit()
            flash('Team member added!')
        elif action == 'edit':
            member_id = request.form['member_id']
            member = TeamMember.query.get(member_id)
            if member:
                member.name = request.form['name']
                member.email = request.form['email']
                member.contact_number = request.form['contact_number']
                member.role = request.form.get('role')
                db.session.commit()
                flash('Team member updated!')
        elif action == 'delete':
            member_id = request.form['member_id']
            member = TeamMember.query.get(member_id)
            if member:
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
    members = TeamMember.query.all()
    return render_template('team_details.html', members=members)
