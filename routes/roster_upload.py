
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import pandas as pd
from werkzeug.utils import secure_filename
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

roster_upload_bp = Blueprint('roster_upload', __name__)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

@roster_upload_bp.route('/roster-upload', methods=['GET', 'POST'])
@login_required
def roster_upload():
    table_data = None
    if request.method == 'POST':
        try:
            from flask_login import current_user
            logger.info(f"[UPLOAD] user={getattr(current_user, 'username', None)}, role={getattr(current_user, 'role', None)}")
            feedback_msgs = []
            if current_user.role not in ['super_admin', 'account_admin', 'team_admin']:
                feedback_msgs.append('You do not have permission to upload shift roster.')
                logger.warning('Permission denied for upload.')
            else:
                file = request.files.get('file')
                if not file:
                    feedback_msgs.append('No file selected.')
                    logger.warning('No file selected for upload.')
                elif not file.filename.endswith('.xlsx'):
                    feedback_msgs.append('Please upload a valid .xlsx file')
                    logger.warning('Invalid file type uploaded.')
                else:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(filepath)
                    logger.info(f"File saved to {filepath}")
                    try:
                        df = pd.read_excel(filepath)
                    except Exception as e:
                        feedback_msgs.append(f'Error reading Excel file: {e}')
                        logger.error(f'Error reading Excel file: {e}')
                        os.remove(filepath)
                        for msg in feedback_msgs:
                            flash(msg)
                        return redirect(url_for('roster_upload.roster_upload'))
                    # Flatten matrix format: each cell becomes a row
                    from models.models import ShiftRoster, TeamMember, db
                    saved_count = 0
                    error_msgs = []
                    # Permission check for team admin
                    if current_user.role == 'team_admin':
                        allowed_account = current_user.account_id
                        allowed_team = current_user.team_id
                    else:
                        allowed_account = None
                        allowed_team = None
                    from datetime import datetime
                    matrix_summary = []
                    # Assume first column is member name, first row is date headers
                    date_columns = list(df.columns)[1:]
                    from flask import session
                    selected_account_id = session.get('selected_account_id')
                    selected_team_id = session.get('selected_team_id')
                    flash(f"Upload using selected_account_id={selected_account_id}, selected_team_id={selected_team_id}, user_account_id={current_user.account_id}, user_team_id={current_user.team_id}")
                    for row_idx, row in df.iterrows():
                        member_name = row[0]
                        for col_idx, date_raw in enumerate(date_columns):
                            shift_code = row[date_raw]
                            if pd.isna(shift_code) or str(shift_code).strip() == '':
                                continue
                            # Parse date
                            date = None
                            try:
                                if isinstance(date_raw, str) and '-' in date_raw:
                                    date = datetime.strptime(date_raw, '%d-%m-%Y').date()
                                else:
                                    date = pd.to_datetime(date_raw).date()
                            except Exception as e:
                                error_msgs.append(f"Row {row_idx+1}, Col {col_idx+2}: Invalid date header '{date_raw}': {e}")
                                logger.warning(f"Row {row_idx+1}, Col {col_idx+2}: Invalid date header '{date_raw}': {e}")
                                continue
                            # Use selected account/team from session if available, else fallback to user
                            account_id = selected_account_id if selected_account_id is not None else current_user.account_id
                            team_id = selected_team_id if selected_team_id is not None else current_user.team_id
                            logger.info(f"[CELL] date={date}, member_name={member_name}, shift_code={shift_code}, account_id={account_id}, team_id={team_id}")
                            # Team admin can only upload for their own account/team
                            if current_user.role == 'team_admin' and (int(account_id) != allowed_account or int(team_id) != allowed_team):
                                error_msgs.append(f"Row {row_idx+1}, Col {col_idx+2}: You do not have permission to upload for account/team {account_id}/{team_id}.")
                                logger.warning(f"Row {row_idx+1}, Col {col_idx+2}: Permission denied for account/team {account_id}/{team_id}.")
                                continue
                            member = TeamMember.query.filter_by(name=member_name, account_id=account_id, team_id=team_id).first()
                            if not member:
                                # Auto-create missing team member
                                try:
                                    member = TeamMember(name=member_name, account_id=account_id, team_id=team_id)
                                    db.session.add(member)
                                    db.session.flush()  # Get member.id
                                    logger.info(f"Created new team member: {member_name} for account_id={account_id}, team_id={team_id}")
                                    flash(f"Created new team member: {member_name} for account_id={account_id}, team_id={team_id}")
                                    matrix_summary.append(f"Row {row_idx+1}, Col {col_idx+2}: Created new team member '{member_name}' for account/team.")
                                except Exception as e:
                                    error_msgs.append(f"Row {row_idx+1}, Col {col_idx+2}: Error creating team member '{member_name}': {e}")
                                    logger.error(f"Row {row_idx+1}, Col {col_idx+2}: Error creating team member '{member_name}': {e}")
                                    continue
                            # Check for duplicate entry
                            existing = ShiftRoster.query.filter_by(date=date, team_member_id=member.id, account_id=account_id, team_id=team_id).first()
                            if existing:
                                error_msgs.append(f"Row {row_idx+1}, Col {col_idx+2}: Duplicate entry for {member_name} on {date}.")
                                logger.warning(f"Row {row_idx+1}, Col {col_idx+2}: Duplicate entry for {member_name} on {date}.")
                                continue
                            try:
                                roster = ShiftRoster(date=date, team_member_id=member.id, shift_code=str(shift_code), account_id=account_id, team_id=team_id)
                                db.session.add(roster)
                                saved_count += 1
                                logger.info(f"Row {row_idx+1}, Col {col_idx+2}: Saved roster entry for {member_name} on {date}.")
                                flash(f"Saved roster entry for {member_name} on {date} (account_id={account_id}, team_id={team_id})")
                                matrix_summary.append(f"Row {row_idx+1}, Col {col_idx+2}: date={date}, member_name={member_name}, shift_code={shift_code}, account_id={account_id}, team_id={team_id}")
                            except Exception as e:
                                error_msgs.append(f"Row {row_idx+1}, Col {col_idx+2}: Error saving cell: {e}")
                                logger.error(f"Row {row_idx+1}, Col {col_idx+2}: Error saving cell: {e}")
                    flash(f"Upload attempted for account_id={account_id}, team_id={team_id}, user={getattr(current_user, 'username', None)}.")
                    if saved_count > 0:
                        db.session.commit()
                        feedback_msgs.append(f"{saved_count} shift roster cells uploaded and saved successfully!")
                        logger.info(f"{saved_count} shift roster cells uploaded and saved successfully!")
                        flash("Upload summary:")
                        for line in matrix_summary:
                            flash(line)
                    else:
                        feedback_msgs.append("No valid cells were saved.")
                        logger.warning("No valid cells were saved.")
                        flash("Upload summary:")
                        for line in matrix_summary:
                            flash(line)
                    if error_msgs:
                        feedback_msgs.extend(error_msgs)
                    os.remove(filepath)
                    logger.info(f"File {filepath} removed after processing.")
            for msg in feedback_msgs:
                flash(msg)
            # Always redirect after POST so flash messages are visible
            return redirect(url_for('roster.roster'))
        except Exception as e:
            logger.error(f"Unexpected error in upload handler: {e}")
            from models.models import db
            db.session.rollback()
            flash(f"Unexpected error: {e}")
            return redirect(url_for('roster_upload.roster_upload'))
    return render_template('shift_roster_upload.html', table_data=table_data)
