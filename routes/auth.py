
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.models import User, Account, Team

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    accounts = Account.query.all()
    selected_account_id = request.form.get('account_id')
    selected_team_id = request.form.get('team_id')
    teams = []
    if selected_account_id:
        teams = Team.query.filter_by(account_id=selected_account_id).all()

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and selected_account_id and selected_team_id:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, account_id=selected_account_id, team_id=selected_team_id).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html', accounts=accounts, teams=teams, selected_account_id=selected_account_id, selected_team_id=selected_team_id)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
