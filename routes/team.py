from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import TeamMember
from app import db

team_bp = Blueprint('team', __name__)

@team_bp.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        role = request.form.get('role')
        member = TeamMember(name=name, email=email, contact_number=contact_number, role=role)
        db.session.add(member)
        db.session.commit()
        flash('Team member added!')
        return redirect(url_for('team.team'))
    members = TeamMember.query.all()
    return render_template('team_details.html', members=members)
