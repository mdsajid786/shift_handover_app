from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import os
import pandas as pd

UPLOAD_FOLDER = 'uploads/escalation_matrix'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

escalation_bp = Blueprint('escalation_matrix', __name__)

@escalation_bp.route('/escalation-matrix', methods=['GET', 'POST'])
@login_required
def escalation_matrix():
    app_names = []
    matrix_data = None
    selected_app = request.args.get('application')
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            flash('Escalation matrix uploaded successfully!')
            return redirect(url_for('escalation_matrix.escalation_matrix'))
        else:
            flash('Please upload a valid .xlsx file.')
    # Find the latest uploaded file
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.xlsx')]
    if files:
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_FOLDER, f)))
        xls = pd.ExcelFile(os.path.join(UPLOAD_FOLDER, latest_file))
        app_names = xls.sheet_names
        if selected_app and selected_app in app_names:
            matrix_data = xls.parse(selected_app).to_dict(orient='records')
    return render_template('escalation_matrix.html', app_names=app_names, matrix_data=matrix_data, selected_app=selected_app)
