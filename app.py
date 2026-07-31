from flask import Flask, session, redirect, url_for, request, render_template
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
from modules.professional_dashboard import pro_bp
from modules.diet_management import pro_diet_bp
from modules.workout_management import pro_workout_bp
from modules.transformation_management import pro_transformations_bp
from modules.earnings_management import pro_earnings_bp
from modules.schedule_management import pro_schedule_bp, user_schedule_bp
from modules.user_reminders import user_reminders_bp
from modules.coaching_packages import coaching_packages_bp
import os


from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Secret key for Flask sessions — read from environment variable in production
app.secret_key = os.getenv("SECRET_KEY", "goalfit_secret_key")

# Database configurations read from environment variables with local defaults
app.config['DB_HOST'] = os.getenv("DB_HOST", "localhost")
app.config['DB_USER'] = os.getenv("DB_USER", "root")
app.config['DB_PASSWORD'] = os.getenv("DB_PASSWORD", "hmpandya528@")
app.config['DB_NAME'] = os.getenv("DB_NAME", "goalfit_ai")
app.config['DB_PORT'] = int(os.getenv("DB_PORT", 3306))

# Ensure required upload directories exist on startup
os.makedirs('static/images/progress_photos', exist_ok=True)
os.makedirs('static/images/diet', exist_ok=True)

# Performance: Gzip compression & Static Asset Caching
import gzip
from io import BytesIO

@app.after_request
def optimize_response(response):
    # Set cache headers for static files
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    
    # Gzip compress text, json, html, css, js responses
    if (response.status_code >= 200 and response.status_code < 300 
        and not response.direct_passthrough 
        and 'Content-Encoding' not in response.headers):
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding.lower():
            content_type = response.content_type or ''
            if any(ct in content_type for ct in ['text/', 'application/json', 'application/javascript', 'text/css']):
                data = response.get_data()
                if len(data) > 500:
                    gzip_buffer = BytesIO()
                    with gzip.GzipFile(mode='wb', fileobj=gzip_buffer, compresslevel=6) as gzip_file:
                        gzip_file.write(data)
                    compressed_data = gzip_buffer.getvalue()
                    response.set_data(compressed_data)
                    response.headers['Content-Encoding'] = 'gzip'
                    response.headers['Content-Length'] = len(compressed_data)
                    response.headers['Vary'] = 'Accept-Encoding'

    return response

def init_db_on_startup():
    """Automatic database schema & seed data initialization check on app startup"""
    try:
        from database.db_connection import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SHOW TABLES;")
            raw_tables = cursor.fetchall()
            tables = [list(r.values())[0].lower() for r in raw_tables] if raw_tables else []
            
            required_tables = ['users', 'professionals', 'chat_messages', 'notifications', 'professional_coaching_packages', 'user_reminders']
            missing_tables = [t for t in required_tables if t not in tables]
            
            needs_init = False
            if missing_tables:
                print(f"[Auto-Init DB] Missing required tables: {missing_tables}. Creating schema and seeding data...")
                needs_init = True
            else:
                cursor.execute("SELECT COUNT(*) as cnt FROM users;")
                row = cursor.fetchone()
                if not row or row['cnt'] == 0:
                    print("[Auto-Init DB] Database users table empty. Seeding demo data...")
                    needs_init = True

            cursor.close()
            conn.close()

            if needs_init:
                from setup_db import create_schema
                from seed_data import seed
                create_schema()
                seed()
                print("[Auto-Init DB] Schema & seed data initialized successfully!")
            else:
                print("[Auto-Init DB] All required database tables verified.")
    except Exception as err:
        print(f"[Auto-Init DB Error] {err}")

# Execute database check on app load
init_db_on_startup()

# Initialize Limiter with generous limits for background polling
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5000 per day", "2000 per hour"],
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
app.register_blueprint(pro_bp)
app.register_blueprint(pro_diet_bp)
app.register_blueprint(pro_workout_bp)
app.register_blueprint(pro_transformations_bp)
app.register_blueprint(pro_earnings_bp)
app.register_blueprint(pro_schedule_bp)
app.register_blueprint(user_schedule_bp)
app.register_blueprint(user_reminders_bp)
app.register_blueprint(coaching_packages_bp)

# Exempt real-time polling blueprints from rate limits
limiter.exempt(chat_bp)
limiter.exempt(user_reminders_bp)

@app.context_processor
def inject_user_hired_pro():
    if 'user_id' in session and session.get('role') == 'user':
        try:
            from database.db_connection import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.id as professional_id, p.full_name as prof_name, p.role as prof_role, p.profile_photo as prof_photo
                FROM client_assignments ca
                JOIN professionals p ON ca.professional_id = p.id
                WHERE ca.user_id = %s AND ca.status = 'active'
                LIMIT 1
            """, (session['user_id'],))
            pro = cursor.fetchone()
            
            user_unread_count = 0
            try:
                from setup_db import ensure_notifications_table
                ensure_notifications_table(cursor)
                cursor.execute("SELECT COUNT(*) as cnt FROM notifications WHERE user_id = %s AND is_read = FALSE", (session['user_id'],))
                n_row = cursor.fetchone()
                user_unread_count = n_row['cnt'] if n_row else 0
            except Exception:
                pass
            
            cursor.close()
            conn.close()
            return dict(hired_pro=pro, user_unread_count=user_unread_count)
        except Exception:
            pass
    return dict(hired_pro=None, user_unread_count=0)


# First-time login protection
@app.before_request
def check_first_login():
    """Redirect first-time users to health profile"""
    if session.get('first_time_login'):
        # Allow only health form, auth routes, and static files
        allowed_routes = ['health.health_profile', 'auth.logout', 'static', 'professional_auth.login', 'professional_auth.register']
        if request.endpoint and request.endpoint not in allowed_routes and not request.endpoint.startswith('professional_auth.'):
            return redirect(url_for('health.health_profile'))


@app.route('/user/notifications')
@app.route('/notifications')
def notifications_redirect():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') in ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_both', 'prof_dietician', 'admin']:
        return redirect('/pro/notifications')
        
    user_id = session['user_id']
    notifs = []
    try:
        from database.db_connection import get_db_connection
        from setup_db import ensure_notifications_table
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            ensure_notifications_table(cursor)
            cursor.execute("""
                SELECT * FROM notifications 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (user_id,))
            notifs = cursor.fetchall() or []
            
            cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print("Notifications fetch warning:", e)
    
    return render_template('user/notifications.html', notifications=notifs)


@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif session.get('role') in ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_both', 'prof_dietician']:
            return redirect(url_for('pro_bp.dashboard'))
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
        if 'is_premium' in session:
            is_premium = session['is_premium']
        else:
            try:
                from database.db_connection import get_db_connection
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM client_assignments WHERE user_id=%s AND status='active'", (session['user_id'],))
                    if cursor.fetchone():
                        is_premium = True
                    cursor.close()
                    conn.close()
                    session['is_premium'] = is_premium
            except Exception:
                is_premium = False
        
    return {
        'current_role': session.get('role', 'user'),
        'is_admin': session.get('role') == 'admin',
        'is_premium': is_premium
    }


if __name__ == '__main__':
    # Bind to PORT provided by host environment (e.g., Render) or default to 5000 for local dev
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(debug=debug, host='0.0.0.0', port=port)