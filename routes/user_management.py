from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User

user_mgmt_bp = Blueprint('user_mgmt', __name__)

@user_mgmt_bp.route('/user-management', methods=['GET', 'POST'])
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('You do not have permission to access user management.')
        return redirect(url_for('dashboard.dashboard'))
    users = User.query.all()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            if username and password and role:
                if User.query.filter_by(username=username).first():
                    flash('Username already exists.')
                else:
                    user = User(username=username, password=password, role=role)
                    db.session.add(user)
                    db.session.commit()
                    flash('User added successfully.')
            else:
                flash('All fields are required.')
        elif action == 'delete':
            user_id = request.form.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user and user.username != 'admin':
                    db.session.delete(user)
                    db.session.commit()
                    flash('User deleted successfully.')
                else:
                    flash('Cannot delete this user.')
        elif action == 'update':
            user_id = request.form.get('user_id')
            role = request.form.get('role')
            if user_id and role:
                user = User.query.get(user_id)
                if user:
                    user.role = role
                    db.session.commit()
                    flash('User role updated.')
    users = User.query.all()
    return render_template('user_management.html', users=users)
