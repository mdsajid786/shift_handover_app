
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User, Account, Team
from werkzeug.security import generate_password_hash

user_mgmt_bp = Blueprint('user_mgmt', __name__)

@user_mgmt_bp.route('/user-management', methods=['GET', 'POST'])
@login_required
def user_management():
    # Role-based filtering
    if current_user.role == 'super_admin':
        users = User.query.all()
        accounts = Account.query.all()
        teams = Team.query.all()
    elif current_user.role == 'account_admin':
        users = User.query.filter_by(account_id=current_user.account_id).all()
        accounts = [Account.query.get(current_user.account_id)]
        teams = Team.query.filter_by(account_id=current_user.account_id).all()
    elif current_user.role == 'team_admin':
        users = User.query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id).all()
        accounts = [Account.query.get(current_user.account_id)]
        teams = [Team.query.get(current_user.team_id)]
    else:
        flash('You do not have permission to access user management.')
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            account_id = request.form.get('account_id', type=int)
            team_id = request.form.get('team_id', type=int)
            if username and password and role and account_id:
                if User.query.filter_by(username=username).first():
                    flash('Username already exists.')
                else:
                    # Only allow adding within scope
                    if current_user.role == 'super_admin' or \
                       (current_user.role == 'account_admin' and account_id == current_user.account_id) or \
                       (current_user.role == 'team_admin' and account_id == current_user.account_id and team_id == current_user.team_id):
                        user = User(username=username, password=generate_password_hash(password), role=role, account_id=account_id, team_id=team_id if team_id else None)
                        db.session.add(user)
                        db.session.commit()
                        flash('User added successfully.')
                    else:
                        flash('You do not have permission to add user to this account/team.')
            else:
                flash('All fields except team are required.')
        elif action == 'delete':
            user_id = request.form.get('user_id', type=int)
            user = User.query.get(user_id)
            if user and user.username != 'admin':
                # Only allow deleting within scope
                if current_user.role == 'super_admin' or \
                   (current_user.role == 'account_admin' and user.account_id == current_user.account_id) or \
                   (current_user.role == 'team_admin' and user.account_id == current_user.account_id and user.team_id == current_user.team_id):
                    db.session.delete(user)
                    db.session.commit()
                    flash('User deleted successfully.')
                else:
                    flash('You do not have permission to delete this user.')
            else:
                flash('Cannot delete this user.')
        elif action == 'update':
            user_id = request.form.get('user_id', type=int)
            role = request.form.get('role')
            user = User.query.get(user_id)
            if user:
                # Only allow updating within scope
                if current_user.role == 'super_admin' or \
                   (current_user.role == 'account_admin' and user.account_id == current_user.account_id) or \
                   (current_user.role == 'team_admin' and user.account_id == current_user.account_id and user.team_id == current_user.team_id):
                    user.role = role
                    db.session.commit()
                    flash('User role updated.')
                else:
                    flash('You do not have permission to update this user.')
    # Refresh users after changes
    if current_user.role == 'super_admin':
        users = User.query.all()
    elif current_user.role == 'account_admin':
        users = User.query.filter_by(account_id=current_user.account_id).all()
    elif current_user.role == 'team_admin':
        users = User.query.filter_by(account_id=current_user.account_id, team_id=current_user.team_id).all()
    return render_template('user_management.html', users=users, accounts=accounts, teams=teams)
