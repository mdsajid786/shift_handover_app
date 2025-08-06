from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Static credentials
        if username == 'admin' and password == 'admin':
            user = User.query.filter_by(username='admin').first()
            if not user:
                user = User(username='admin', password='admin')
                from app import db
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
