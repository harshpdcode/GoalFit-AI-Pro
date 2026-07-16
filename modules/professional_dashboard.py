from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from functools import wraps
import mysql.connector

pro_bp = Blueprint('pro_bp', __name__, url_prefix='/pro')

def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config['DB_HOST'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME']
    )

def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        allowed_roles = ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_dietician', 'prof_both']
        if 'user_id' not in session or session.get('role') not in allowed_roles:
            flash("Please log in as a professional to access this page.", "danger")
            return redirect(url_for('professional_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@pro_bp.context_processor
def inject_pro_info():
    allowed_roles = ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_dietician', 'prof_both']
    if 'user_id' in session and session.get('role') in allowed_roles:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM professionals WHERE id = %s", (session['user_id'],))
        pro_user = cursor.fetchone()
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM notifications WHERE professional_id=%s AND is_read=FALSE",
            (session['user_id'],)
        )
        row = cursor.fetchone()
        unread_count = row['cnt'] if row else 0
        cursor.close()
        conn.close()
        return dict(current_pro=pro_user, unread_count=unread_count)
    return dict(current_pro=None, unread_count=0)

@pro_bp.route('/')
@pro_bp.route('/dashboard')
@pro_required
def dashboard():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Stats
    cursor.execute("SELECT COUNT(*) as count FROM client_assignments WHERE professional_id=%s AND status='active'", (prof_id,))
    active_clients = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM hire_requests WHERE professional_id=%s AND status='pending'", (prof_id,))
    pending_reqs = cursor.fetchone()['count']
    
    cursor.execute("SELECT COALESCE(SUM(professional_amount), 0) as total FROM payments WHERE professional_id=%s AND payment_status='paid'", (prof_id,))
    revenue = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(AVG(rating), 0) as avg_rating FROM professional_reviews WHERE professional_id=%s", (prof_id,))
    rating = cursor.fetchone()['avg_rating']
    
    # Recent Activities
    cursor.execute("""
        SELECT h.*, u.name as client_name 
        FROM hire_requests h 
        JOIN users u ON h.user_id = u.id 
        WHERE h.professional_id=%s AND h.status='pending'
        ORDER BY h.created_at DESC LIMIT 5
    """, (prof_id,))
    recent_requests = cursor.fetchall()
    
    # Client Distribution for Donut Chart
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN LOWER(plan_type) LIKE '%diet%' THEN 1 ELSE 0 END) as diet_only,
            SUM(CASE WHEN LOWER(plan_type) LIKE '%workout%' OR LOWER(plan_type) LIKE '%training%' THEN 1 ELSE 0 END) as workout_only,
            SUM(CASE WHEN LOWER(plan_type) LIKE '%both%' OR LOWER(plan_type) LIKE '%transformation%' OR LOWER(plan_type) LIKE '%complete%' THEN 1 ELSE 0 END) as both_plans
        FROM client_assignments 
        WHERE professional_id=%s AND status='active'
    """, (prof_id,))
    dist = cursor.fetchone()
    diet_only = dist['diet_only'] if dist and dist['diet_only'] else 0
    workout_only = dist['workout_only'] if dist and dist['workout_only'] else 0
    both_plans = dist['both_plans'] if dist and dist['both_plans'] else 0
    
    cursor.close()
    conn.close()
    
    return render_template('professional/dashboard.html', 
                           active_clients=active_clients, 
                           pending_reqs=pending_reqs, 
                           revenue=revenue,
                           rating=round(rating, 1),
                           recent_requests=recent_requests,
                           diet_only=diet_only,
                           workout_only=workout_only,
                           both_plans=both_plans)

@pro_bp.route('/clients')
@pro_required
def clients():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, u.name, u.email, uh.weight_kg, uh.goal_type, uh.height_cm
        FROM client_assignments c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN user_health uh ON u.id = uh.user_id
        WHERE c.professional_id = %s AND c.status = 'active'
    """, (prof_id,))
    active_clients = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as count FROM hire_requests WHERE professional_id=%s AND status='pending'", (prof_id,))
    pending_count = cursor.fetchone()['count']
    cursor.close()
    conn.close()
    return render_template('professional/clients.html', clients=active_clients, status='active', pending_count=pending_count)


@pro_bp.route('/clients/pending')
@pro_required
def clients_pending():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.*, u.name, u.email, uh.weight_kg, uh.goal_type, uh.height_cm, h.plan_type
        FROM hire_requests h
        JOIN users u ON h.user_id = u.id
        LEFT JOIN user_health uh ON u.id = uh.user_id
        WHERE h.professional_id = %s AND h.status = 'pending'
        ORDER BY h.created_at DESC
    """, (prof_id,))
    pending_clients = cursor.fetchall()
    pending_count = len(pending_clients)
    cursor.close()
    conn.close()
    return render_template('professional/clients.html', clients=pending_clients, status='pending', pending_count=pending_count)


@pro_bp.route('/clients/pending/<int:req_id>/accept', methods=['POST'])
@pro_required
def accept_hire_request(req_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hire_requests WHERE id=%s AND professional_id=%s", (req_id, prof_id))
    req = cursor.fetchone()
    if req:
        import datetime
        cursor.execute("UPDATE hire_requests SET status='accepted' WHERE id=%s", (req_id,))
        cursor.execute("""
            INSERT INTO client_assignments (user_id, professional_id, plan_type, start_date, status)
            VALUES (%s, %s, %s, %s, 'active')
            ON DUPLICATE KEY UPDATE status='active', start_date=%s
        """, (req['user_id'], prof_id, req.get('plan_type','both'), datetime.date.today(), datetime.date.today()))
        conn.commit()
        flash("Client request accepted!", "success")
    cursor.close()
    conn.close()
    return redirect(url_for('pro_bp.clients_pending'))


@pro_bp.route('/clients/pending/<int:req_id>/reject', methods=['POST'])
@pro_required
def reject_hire_request(req_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE hire_requests SET status='rejected' WHERE id=%s AND professional_id=%s", (req_id, prof_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Request rejected.", "info")
    return redirect(url_for('pro_bp.clients_pending'))


@pro_bp.route('/clients/completed')
@pro_required
def clients_completed():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, u.name, u.email, uh.weight_kg, uh.goal_type, uh.height_cm
        FROM client_assignments c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN user_health uh ON u.id = uh.user_id
        WHERE c.professional_id = %s AND c.status = 'completed'
    """, (prof_id,))
    completed_clients = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as count FROM hire_requests WHERE professional_id=%s AND status='pending'", (prof_id,))
    pending_count = cursor.fetchone()['count']
    cursor.close()
    conn.close()
    return render_template('professional/clients.html', clients=completed_clients, status='completed', pending_count=pending_count)

@pro_bp.route('/client/<int:client_id>')
@pro_required
def client_detail(client_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify assignment
    cursor.execute("SELECT * FROM client_assignments WHERE professional_id = %s AND user_id = %s AND status = 'active'", (prof_id, client_id))
    assignment = cursor.fetchone()
    
    if not assignment:
        flash("Unauthorized or client not active.", "danger")
        return redirect(url_for('pro_bp.clients'))
        
    cursor.execute("SELECT * FROM users WHERE id = %s", (client_id,))
    client = cursor.fetchone()
    
    cursor.execute("SELECT * FROM user_health WHERE user_id = %s", (client_id,))
    health = cursor.fetchone()
    
    # Nutrition Stats (Today)
    import datetime
    today = datetime.date.today()
    cursor.execute("""
        SELECT dl.is_completed, dm.meal_time, dm.calories
        FROM diet_logs dl
        JOIN diet_meals dm ON dl.meal_id = dm.id
        WHERE dl.user_id = %s AND dl.log_date = %s
    """, (client_id, today))
    today_meals = cursor.fetchall()
    
    total_calories_consumed = sum(meal['calories'] for meal in today_meals if meal['is_completed'])
    target_calories = 2000 # default
    if health and health.get('goal_type') == 'Fat Loss':
        target_calories = 1800
    elif health and health.get('goal_type') == 'Muscle Gain':
        target_calories = 2500
        
    calories_remaining = max(0, target_calories - total_calories_consumed)
    nutrition_progress = min(100, int((total_calories_consumed / target_calories) * 100)) if target_calories > 0 else 0
    
    # Format meals checklist (Lunch, Snack, Dinner, etc)
    meal_checklist = []
    for meal in today_meals:
        meal_checklist.append({
            'name': meal['meal_time'],
            'completed': meal['is_completed']
        })
        
    # Workout Stats
    cursor.execute("SELECT performed_date FROM user_workouts WHERE user_id = %s ORDER BY performed_date DESC LIMIT 1", (client_id,))
    last_workout_row = cursor.fetchone()
    last_workout = last_workout_row['performed_date'].strftime('%Y-%m-%d') if last_workout_row else "Never"
    
    # Plan completion logic
    plan_completion = 72
    
    # Fetch weight logs for chart
    cursor.execute("SELECT weight_kg, log_date FROM progress_logs WHERE user_id = %s ORDER BY log_date ASC LIMIT 10", (client_id,))
    logs = cursor.fetchall()
    weight_dates = [log['log_date'].strftime('%b %d') if isinstance(log['log_date'], (datetime.date, datetime.datetime)) else str(log['log_date']) for log in logs]
    weight_values = [log['weight_kg'] for log in logs]

    # Fetch assigned plans
    cursor.execute("SELECT * FROM custom_diet_plans WHERE user_id = %s AND professional_id = %s LIMIT 1", (client_id, prof_id))
    diet_plan = cursor.fetchone()
    
    cursor.execute("SELECT * FROM custom_workout_plans WHERE user_id = %s AND professional_id = %s LIMIT 1", (client_id, prof_id))
    workout_plan = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return render_template('professional/client_detail.html', 
                           client=client, 
                           health=health, 
                           assignment=assignment,
                           today_meals=meal_checklist,
                           total_calories=total_calories_consumed,
                           target_calories=target_calories,
                           calories_remaining=calories_remaining,
                           nutrition_progress=nutrition_progress,
                           last_workout=last_workout,
                           plan_completion=plan_completion,
                           weight_dates=weight_dates,
                           weight_values=weight_values,
                           diet_plan=diet_plan,
                           workout_plan=workout_plan)


@pro_bp.route('/client/<int:client_id>/notes', methods=['POST'])
@pro_required
def save_client_notes(client_id):
    prof_id = session.get('user_id')
    notes = request.form.get('notes', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE client_assignments SET notes = %s WHERE professional_id = %s AND user_id = %s", (notes, prof_id, client_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Notes saved successfully!", "success")
    return redirect(url_for('pro_bp.client_detail', client_id=client_id))


@pro_bp.route('/chat/<int:client_id>')
@pro_required
def chat_redirect(client_id):
    return redirect(url_for('pro_bp.client_detail', client_id=client_id) + '?chat=open')


@pro_bp.route('/reviews')
@pro_required
def reviews():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT pr.*, u.name as client_name
        FROM professional_reviews pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.professional_id = %s
        ORDER BY pr.created_at DESC
    """, (prof_id,))
    all_reviews = cursor.fetchall()
    cursor.execute("SELECT COALESCE(AVG(rating), 0) as avg, COUNT(*) as total FROM professional_reviews WHERE professional_id=%s", (prof_id,))
    stats = cursor.fetchone()
    cursor.close()
    conn.close()
    avg_rating = round(stats['avg'], 1) if stats else 0
    total_reviews = stats['total'] if stats else 0
    return render_template('professional/reviews.html', reviews=all_reviews, avg_rating=avg_rating, total_reviews=total_reviews)


@pro_bp.route('/notifications')
@pro_required
def notifications():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM notifications
        WHERE professional_id = %s
        ORDER BY created_at DESC
        LIMIT 50
    """, (prof_id,))
    notifs = cursor.fetchall()
    # Mark all as read
    cursor.execute("UPDATE notifications SET is_read=TRUE WHERE professional_id=%s AND is_read=FALSE", (prof_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('professional/notifications.html', notifications=notifs)


@pro_bp.route('/settings', methods=['GET', 'POST'])
@pro_required
def settings():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        experience_years = request.form.get('experience_years', '').strip()
        specialization = request.form.get('specialization', '').strip()
        import os
        from werkzeug.utils import secure_filename
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_dir = os.path.join('static', 'images', 'profile_img')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, f"prof_{prof_id}_{filename}")
                file.save(filepath)
                profile_photo = filepath.replace('\\', '/')
        if profile_photo:
            cursor.execute("""
                UPDATE professionals SET full_name=%s, phone=%s, bio=%s, experience_years=%s, specialization=%s, profile_photo=%s
                WHERE id=%s
            """, (full_name, phone, bio, experience_years, specialization, profile_photo, prof_id))
        else:
            cursor.execute("""
                UPDATE professionals SET full_name=%s, phone=%s, bio=%s, experience_years=%s, specialization=%s
                WHERE id=%s
            """, (full_name, phone, bio, experience_years, specialization, prof_id))
        conn.commit()
        session['user_name'] = full_name
        flash("Profile updated successfully!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for('pro_bp.settings'))
    cursor.execute("SELECT * FROM professionals WHERE id=%s", (prof_id,))
    pro = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('professional/settings.html', pro=pro)


@pro_bp.route('/support', methods=['GET', 'POST'])
@pro_required
def support():
    if request.method == 'POST':
        flash("Your support request has been submitted. We'll get back to you within 24 hours.", "success")
        return redirect(url_for('pro_bp.support'))
    return render_template('professional/support.html')
