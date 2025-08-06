from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

# Import blueprints

from routes.auth import auth_bp
from routes.handover import handover_bp
from routes.dashboard import dashboard_bp
from routes.roster import roster_bp

from routes.team import team_bp
from routes.roster_upload import roster_upload_bp
from routes.reports import reports_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(handover_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(roster_bp)
app.register_blueprint(team_bp)
app.register_blueprint(roster_upload_bp)
app.register_blueprint(reports_bp)

@login_manager.user_loader
def load_user(user_id):
    from models.models import User
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)
