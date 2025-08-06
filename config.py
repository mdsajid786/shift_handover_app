import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://user:password@localhost/shift_handover')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'team@example.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'password')
    TEAM_EMAIL = os.getenv('TEAM_EMAIL', 'team@example.com')
