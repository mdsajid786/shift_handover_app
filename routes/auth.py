

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.models import User, Account, Team
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

from flask import jsonify

# AJAX endpoint to get teams for a selected account
@auth_bp.route('/get_teams')
def get_teams():
    account_id = request.args.get('account_id')
    teams = []
    if account_id:
        teams = Team.query.filter_by(account_id=account_id).all()
    return jsonify({
        'teams': [{'id': t.id, 'name': t.name} for t in teams]
    })


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    accounts = Account.query.all()
    selected_account_id = request.form.get('account_id')
    selected_team_id = request.form.get('team_id')
    # Convert to int if present, else None
    selected_account_id_int = int(selected_account_id) if selected_account_id and selected_account_id.isdigit() else None
    selected_team_id_int = int(selected_team_id) if selected_team_id and selected_team_id.isdigit() else None
    teams = []
    if selected_account_id_int:
        teams = Team.query.filter_by(account_id=selected_account_id_int).all()

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and selected_account_id_int and selected_team_id_int:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, account_id=selected_account_id_int, team_id=selected_team_id_int).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html', accounts=accounts, teams=teams, selected_account_id=selected_account_id_int, selected_team_id=selected_team_id_int)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
