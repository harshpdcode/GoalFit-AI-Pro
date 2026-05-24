from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database.db_connection import get_db_connection
from functools import wraps

trainer_dashboard_bp = Blueprint('trainer_dashboard', __name__, url_prefix='/trainer')

def trainer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        role = session.get('role')
        if role not in ['prof_trainer', 'prof_both']:
            flash("Access restricted to trainers.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@trainer_dashboard_bp.route('/dashboard')
@trainer_required
def dashboard():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Stats
    cursor.execute("SELECT COUNT(*) as total FROM client_assignments WHERE professional_id=%s AND status='active'", (prof_id,))
    active_clients = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(professional_amount) as rev FROM payments WHERE professional_id=%s AND payment_status='paid'", (prof_id,))
    revenue = cursor.fetchone()['rev'] or 0

    cursor.execute("SELECT COUNT(*) as req FROM hire_requests WHERE professional_id=%s AND status='pending'", (prof_id,))
    pending_reqs = cursor.fetchone()['req']

    # Clients
    cursor.execute("""
        SELECT ca.*, u.name, u.email 
        FROM client_assignments ca
        JOIN users u ON ca.user_id = u.id
        WHERE ca.professional_id=%s AND ca.status='active'
    """, (prof_id,))
    clients = cursor.fetchall()

    # Pending requests
    cursor.execute("""
        SELECT hr.*, u.name, u.email 
        FROM hire_requests hr
        JOIN users u ON hr.user_id = u.id
        WHERE hr.professional_id=%s AND hr.status='pending'
    """, (prof_id,))
    requests_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('professional/dashboard_trainer.html',
                           requests=requests_data,
                           clients=clients,
                           active_clients=len(clients),
                           revenue=revenue,
                           pending_reqs=len(requests_data))

@trainer_dashboard_bp.route('/request/<int:req_id>/<action>')
@trainer_required
def handle_request(req_id, action):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hire_requests WHERE id=%s AND professional_id=%s", (req_id, prof_id))
    req = cursor.fetchone()
    
    if req and req['status'] == 'pending':
        if action == 'accept':
            cursor.execute("UPDATE hire_requests SET status='accepted' WHERE id=%s", (req_id,))
            cursor.execute("SELECT duration_days FROM professional_pricing WHERE plan_type=%s AND professional_id=%s", (req['plan_type'], prof_id))
            plan_info = cursor.fetchone()
            duration = plan_info['duration_days'] if plan_info else 30

            cursor.execute("""
                INSERT INTO client_assignments (user_id, professional_id, plan_type, start_date, end_date, status)
                VALUES (%s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), 'active')
            """, (req['user_id'], prof_id, req['plan_type'], duration))
            flash("Request accepted and client assigned.", "success")
        elif action == 'reject':
            cursor.execute("UPDATE hire_requests SET status='rejected' WHERE id=%s", (req_id,))
            flash("Request rejected.", "warning")
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('trainer_dashboard.dashboard'))

@trainer_dashboard_bp.route('/build-plan/<int:client_id>', methods=['GET', 'POST'])
@trainer_required
def build_plan(client_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM client_assignments WHERE professional_id=%s AND user_id=%s AND status='active'", (prof_id, client_id))
    if not cursor.fetchone():
        flash("Unauthorized", "danger")
        return redirect(url_for('trainer_dashboard.dashboard'))

    cursor.execute("SELECT * FROM users WHERE id=%s", (client_id,))
    client_user = cursor.fetchone()

    if request.method == 'POST':
        plan_name = request.form.get('plan_name')
        days = request.form.getlist('day[]')
        workout_ids = request.form.getlist('workout_id[]')
        
        # Ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_workout_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                professional_id INT NOT NULL,
                plan_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_workout_plan_exercises (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plan_id INT NOT NULL,
                workout_day VARCHAR(50) NOT NULL,
                workout_id INT NOT NULL
            )
        """)
        
        cursor.execute("INSERT INTO custom_workout_plans (user_id, professional_id, plan_name) VALUES (%s, %s, %s)", (client_id, prof_id, plan_name))
        plan_id = cursor.lastrowid
        
        for d, w_id in zip(days, workout_ids):
            if w_id:
                cursor.execute("INSERT INTO custom_workout_plan_exercises (plan_id, workout_day, workout_id) VALUES (%s, %s, %s)", (plan_id, d, w_id))
            
        conn.commit()
        flash("Workout plan published successfully!", "success")
        return redirect(url_for('trainer_dashboard.dashboard'))

    # If professional_workouts doesn't exist or is empty, we fall back to generic workout_exercises
    try:
        cursor.execute("SELECT * FROM professional_workouts WHERE professional_id=%s", (prof_id,))
        workouts = cursor.fetchall()
    except:
        # Fallback to general exercises
        cursor.execute("SELECT id, exercise_name as workout_name, target_muscle, 3 as sets, 12 as reps FROM workout_exercises")
        workouts = cursor.fetchall()
        
    cursor.close()
    conn.close()

    return render_template('professional/build_workout.html', client=client_user, client_id=client_id, workouts=workouts)
