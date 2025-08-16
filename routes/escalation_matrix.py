from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
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
        if current_user.role == 'viewer':
            flash('You do not have permission to upload escalation matrix.')
            return redirect(url_for('escalation_matrix.escalation_matrix'))
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            # Save file info to EscalationMatrixFile table
            from models.models import EscalationMatrixFile, db
            import datetime
            matrix_file = EscalationMatrixFile(filename=file.filename, upload_time=datetime.datetime.now())
            db.session.add(matrix_file)
            # Parse and save each sheet/row if you have a model for escalation matrix rows
            xls = pd.ExcelFile(filepath)
            for sheet_name in xls.sheet_names:
                df = xls.parse(sheet_name)
                table_data = df.where(pd.notnull(df), '').to_dict(orient='records')
                # If you have a model like EscalationMatrixRow, save each row
                # from models.models import EscalationMatrixRow
                # for row in table_data:
                #     escalation_row = EscalationMatrixRow(...)
                #     db.session.add(escalation_row)
            db.session.commit()
            flash('Escalation matrix uploaded and saved successfully!')
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
            df = xls.parse(selected_app)
            # Replace NaN/None with empty string for display
            matrix_data = df.where(pd.notnull(df), '').to_dict(orient='records')
    return render_template('escalation_matrix.html', app_names=app_names, matrix_data=matrix_data, selected_app=selected_app)
