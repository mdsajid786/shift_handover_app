from flask_mail import Message
from app import mail
from flask import current_app

def send_handover_email(shift):
    subject = f"Shift Handover Summary for {shift.date}"
    recipients = [current_app.config['TEAM_EMAIL']]
    body = f"Handover summary for shift on {shift.date}."
    msg = Message(subject, recipients=recipients, body=body)
    mail.send(msg)
