from flask import Flask, session, redirect, url_for, request
from modules.auth import auth_bp
from modules.health import health_bp
from modules.bmi import bmi_bp
from modules.prediction import prediction_bp
from modules.diet import diet_bp
from modules.workout import workout_bp
from modules.dashboard import dashboard_bp
from modules.progress import progress_bp
from modules.admin import admin_bp
from modules.water import water_bp
from modules.feedback import feedback_bp
from modules.report import report_bp


app = Flask(__name__)
app.secret_key = "goalfit_secret_key"

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(health_bp)
app.register_blueprint(bmi_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(diet_bp)
app.register_blueprint(workout_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(water_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(report_bp)


# First-time login protection
@app.before_request
def check_first_login():
    """Redirect first-time users to health profile"""
    if session.get('first_time_login'):
        # Allow only health form, auth routes, and static files
        allowed_routes = ['health.health_profile', 'auth.logout', 'static']
        if request.endpoint and request.endpoint not in allowed_routes:
            return redirect(url_for('health.health_profile'))


@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/check-session')
def check_session():
    return str(session)


# Context processor to make session data available in all templates
@app.context_processor
def inject_globals():
    return {
        'current_role': session.get('role', 'user'),
        'is_admin': session.get('role') == 'admin'
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)