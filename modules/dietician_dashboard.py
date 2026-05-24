from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database.db_connection import get_db_connection
from functools import wraps

dietician_dashboard_bp = Blueprint('dietician_dashboard', __name__, url_prefix='/dietician')

def dietician_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        role = session.get('role')
        if role not in ['prof_dietician', 'prof_both']:
            flash("Access restricted to dieticians.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dietician_dashboard_bp.route('/dashboard')
@dietician_required
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

    return render_template('professional/dashboard_dietician.html',
                           requests=requests_data,
                           clients=clients,
                           active_clients=len(clients),
                           revenue=revenue,
                           pending_reqs=len(requests_data))

@dietician_dashboard_bp.route('/request/<int:req_id>/<action>')
@dietician_required
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
    return redirect(url_for('dietician_dashboard.dashboard'))

@dietician_dashboard_bp.route('/build-plan/<int:client_id>', methods=['GET', 'POST'])
@dietician_required
def build_plan(client_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM client_assignments WHERE professional_id=%s AND user_id=%s AND status='active'", (prof_id, client_id))
    if not cursor.fetchone():
        flash("Unauthorized", "danger")
        return redirect(url_for('dietician_dashboard.dashboard'))

    cursor.execute("SELECT * FROM users WHERE id=%s", (client_id,))
    client_user = cursor.fetchone()

    if request.method == 'POST':
        plan_name = request.form.get('plan_name')
        meal_types = request.form.getlist('meal_type[]')
        meal_ids = request.form.getlist('meal_id[]')
        
        # Ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_diet_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                professional_id INT NOT NULL,
                plan_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_diet_plan_meals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plan_id INT NOT NULL,
                meal_type VARCHAR(50) NOT NULL,
                meal_id INT NOT NULL
            )
        """)
        
        cursor.execute("INSERT INTO custom_diet_plans (user_id, professional_id, plan_name) VALUES (%s, %s, %s)", (client_id, prof_id, plan_name))
        plan_id = cursor.lastrowid
        
        for t, m_id in zip(meal_types, meal_ids):
            if m_id:
                cursor.execute("INSERT INTO custom_diet_plan_meals (plan_id, meal_type, meal_id) VALUES (%s, %s, %s)", (plan_id, t, m_id))
            
        conn.commit()
        flash("Diet plan published successfully!", "success")
        return redirect(url_for('dietician_dashboard.dashboard'))

    # Fallback to generic diet_meals
    try:
        cursor.execute("SELECT * FROM professional_meals WHERE professional_id=%s", (prof_id,))
        meals = cursor.fetchall()
    except:
        # Fallback
        cursor.execute("SELECT id, meal_name, calories, protein, carbs, fats FROM diet_meals")
        meals = cursor.fetchall()
        
    cursor.close()
    conn.close()

    return render_template('professional/build_diet.html', client=client_user, client_id=client_id, meals=meals)
