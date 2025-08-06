from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import pandas as pd
from werkzeug.utils import secure_filename
import os

roster_upload_bp = Blueprint('roster_upload', __name__)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

@roster_upload_bp.route('/roster-upload', methods=['GET', 'POST'])
@login_required
def roster_upload():
    table_data = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            df = pd.read_excel(filepath)
            table_data = df.to_dict(orient='records')
            columns = df.columns.tolist()
            os.remove(filepath)
            return render_template('shift_roster_upload.html', table_data=table_data, columns=columns)
        else:
            flash('Please upload a valid .xlsx file')
    return render_template('shift_roster_upload.html', table_data=table_data)
