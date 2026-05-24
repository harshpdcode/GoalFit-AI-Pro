from flask import Flask, session, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
from modules.marketplace import marketplace_bp
from modules.professional_auth import professional_auth_bp
from modules.trainer_dashboard import trainer_dashboard_bp
from modules.dietician_dashboard import dietician_dashboard_bp
from modules.payment_gateway import payment_gateway_bp
from modules.pdf_generator import pdf_generator_bp
from modules.chat import chat_bp
from modules.diet_tracking import diet_tracking_bp
from modules.progress_gallery import progress_gallery_bp


app = Flask(__name__)
app.secret_key = "goalfit_secret_key"

# Initialize Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

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
app.register_blueprint(marketplace_bp)
app.register_blueprint(professional_auth_bp)
app.register_blueprint(trainer_dashboard_bp)
app.register_blueprint(dietician_dashboard_bp)
app.register_blueprint(payment_gateway_bp)
app.register_blueprint(pdf_generator_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(diet_tracking_bp)
app.register_blueprint(progress_gallery_bp)


# First-time login protection
@app.before_request
def check_first_login():
    """Redirect first-time users to health profile"""
    if session.get('first_time_login'):
        # Allow only health form, auth routes, and static files
        allowed_routes = ['health.health_profile', 'auth.logout', 'static', 'professional_auth.login', 'professional_auth.register']
        if request.endpoint and request.endpoint not in allowed_routes and not request.endpoint.startswith('professional_auth.'):
            return redirect(url_for('health.health_profile'))


@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif session.get('role') in ['prof_trainer', 'prof_both']:
            return redirect(url_for('trainer_dashboard.dashboard'))
        elif session.get('role') == 'prof_dietician':
            return redirect(url_for('dietician_dashboard.dashboard'))
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/check-session')
def check_session():
    return str(session)


# Context processor to make session data available in all templates
@app.context_processor
def inject_globals():
    is_premium = False
    if 'user_id' in session and session.get('role') == 'user':
        from database.db_connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM client_assignments WHERE user_id=%s AND status='active'", (session['user_id'],))
        if cursor.fetchone():
            is_premium = True
        cursor.close()
        conn.close()
        
    return {
        'current_role': session.get('role', 'user'),
        'is_admin': session.get('role') == 'admin',
        'is_premium': is_premium
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)