from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Incident, TeamMember, Shift
from app import db
import plotly.graph_objs as go
import plotly
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    open_incidents = Incident.query.filter_by(status='Active').all()
    current_shift = Shift.query.order_by(Shift.date.desc()).first()
    current_engineers = current_shift.current_engineers if current_shift else []
    next_engineers = current_shift.next_engineers if current_shift else []
    # Chart.js/Plotly example
    incident_counts = [len(open_incidents), len(current_engineers), len(next_engineers)]
    labels = ['Open Incidents', 'Current Engineers', 'Next Engineers']
    bar = go.Bar(x=labels, y=incident_counts)
    data = [bar]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', open_incidents=open_incidents, current_engineers=current_engineers, next_engineers=next_engineers, graphJSON=graphJSON)
