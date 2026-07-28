from flask import Blueprint, session, redirect, url_for, render_template, request, flash, jsonify
from database.db_connection import get_db_connection
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import date, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ===== ADMIN REQUIRED DECORATOR =====
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash("Access denied. Admin only.", "danger")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated


# ===== HELPER: Log Activity =====
def log_activity(user_id, action, details=""):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (user_id, action, details) VALUES (%s, %s, %s)",
                (user_id, action, details)
            )
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Activity log error: {e}")


# ================= ONE-CLICK DATABASE SYNC =================
@admin_bp.route('/sync-database', methods=['POST'])
@admin_bp.route('/seed-meals', methods=['POST'])
@admin_required
def sync_database():
    try:
        from setup_db import create_schema
        from seed_data import seed

        # 1. Update schema and ensure all tables exist
        create_schema()

        # 2. Reinsert full demo and trainer datasets according to new features
        seed()

        log_activity(session['user_id'], 'sync_database', 'Triggered full database schema sync & data reinsertion')
        flash("⚡ Database synced & updated with latest trainer & platform data successfully!", "success")
    except Exception as e:
        print(f"Database sync error: {e}")
        flash(f"Database sync error: {e}", "danger")

    return redirect(url_for('admin.admin_dashboard'))


# ================= ADMIN DASHBOARD =================
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    total_users = 0
    new_this_week = 0
    total_professionals = 0
    total_revenue = 0
    total_gross_volume = 0
    total_hire_requests = 0
    total_active_assignments = 0
    avg_bmi = 0
    total_meals = 0
    total_exercises = 0
    total_packages = 0
    unread_feedback = 0

    try:
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='user'")
        r = cursor.fetchone()
        total_users = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as new_week FROM users WHERE role='user' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        r = cursor.fetchone()
        new_this_week = r['new_week'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM professionals")
        r = cursor.fetchone()
        total_professionals = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT SUM(commission_amount) as rev, SUM(amount) as gross FROM payments WHERE payment_status='paid'")
        r = cursor.fetchone()
        if r:
            total_revenue = round(r['rev'] or 0, 2)
            total_gross_volume = round(r['gross'] or 0, 2)
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM hire_requests")
        r = cursor.fetchone()
        total_hire_requests = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM client_assignments WHERE status='active'")
        r = cursor.fetchone()
        total_active_assignments = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM professional_coaching_packages")
        r = cursor.fetchone()
        total_packages = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("""
            SELECT ROUND(AVG(bmi_value), 1) as avg_bmi 
            FROM bmi_records br
            INNER JOIN (
                SELECT user_id, MAX(recorded_date) as latest 
                FROM bmi_records GROUP BY user_id
            ) lb ON br.user_id = lb.user_id AND br.recorded_date = lb.latest
        """)
        r = cursor.fetchone()
        avg_bmi = r['avg_bmi'] if r and r['avg_bmi'] else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM diet_meals")
        r = cursor.fetchone()
        total_meals = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as total FROM workout_exercises")
        r = cursor.fetchone()
        total_exercises = r['total'] if r else 0
    except Exception:
        pass

    try:
        cursor.execute("SELECT COUNT(*) as unread FROM user_feedback WHERE status='unread'")
        r = cursor.fetchone()
        unread_feedback = r['unread'] if r else 0
    except Exception:
        pass

    # Goal type distribution
    goal_dist = []
    try:
        cursor.execute("""
            SELECT goal_type, COUNT(*) as count FROM user_health 
            GROUP BY goal_type
        """)
        goal_dist = cursor.fetchall() or []
    except Exception:
        pass

    # Diet preference distribution
    diet_dist = []
    try:
        cursor.execute("""
            SELECT diet_preference, COUNT(*) as count FROM user_health 
            GROUP BY diet_preference
        """)
        diet_dist = cursor.fetchall() or []
    except Exception:
        pass

    # Recent activity logs
    recent_logs = []
    try:
        cursor.execute("""
            SELECT al.*, u.name as user_name 
            FROM activity_logs al 
            LEFT JOIN users u ON al.user_id = u.id 
            ORDER BY al.created_at DESC LIMIT 10
        """)
        recent_logs = cursor.fetchall() or []
    except Exception:
        pass

    import datetime
    today = datetime.date.today()

    # User growth (last 30 days continuous series)
    raw_user_growth = []
    try:
        cursor.execute("""
            SELECT DATE(created_at) as reg_date, COUNT(*) as count 
            FROM users WHERE role='user' AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at) 
            ORDER BY reg_date ASC
        """)
        raw_user_growth = cursor.fetchall() or []
    except Exception:
        pass

    user_map = { (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d'): 0 for i in range(29, -1, -1) }
    for r in raw_user_growth:
        if r.get('reg_date'):
            d_str = str(r['reg_date'])
            if d_str in user_map:
                user_map[d_str] = int(r['count'] or 0)

    user_growth = [
        {'reg_date': d_str, 'count': cnt, 'formatted_date': datetime.datetime.strptime(d_str, '%Y-%m-%d').strftime('%b %d')}
        for d_str, cnt in user_map.items()
    ]

    # Payment growth (last 30 days continuous series)
    raw_payment_growth = []
    try:
        cursor.execute("""
            SELECT DATE(created_at) as pay_date, SUM(commission_amount) as daily_revenue 
            FROM payments WHERE payment_status='paid' AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at) 
            ORDER BY pay_date ASC
        """)
        raw_payment_growth = cursor.fetchall() or []
    except Exception:
        pass

    pay_map = { (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d'): 0.0 for i in range(29, -1, -1) }
    for r in raw_payment_growth:
        if r.get('pay_date'):
            d_str = str(r['pay_date'])
            if d_str in pay_map:
                pay_map[d_str] = round(float(r['daily_revenue'] or 0), 2)

    payment_growth = [
        {'pay_date': d_str, 'daily_revenue': rev, 'formatted_date': datetime.datetime.strptime(d_str, '%Y-%m-%d').strftime('%b %d')}
        for d_str, rev in pay_map.items()
    ]

    cursor.close()
    conn.close()

    return render_template('admin/admin_dashboard.html',
        total_users=total_users,
        new_this_week=new_this_week,
        total_professionals=total_professionals,
        total_revenue=total_revenue,
        total_gross_volume=total_gross_volume,
        total_hire_requests=total_hire_requests,
        total_active_assignments=total_active_assignments,
        total_packages=total_packages,
        avg_bmi=avg_bmi,
        total_meals=total_meals,
        total_exercises=total_exercises,
        unread_feedback=unread_feedback,
        goal_dist=goal_dist,
        diet_dist=diet_dist,
        recent_logs=recent_logs,
        user_growth=user_growth,
        payment_growth=payment_growth
    )


# ================= USER MANAGEMENT =================
@admin_bp.route('/users')
@admin_required
def user_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    search = request.args.get('search', '')
    
    if search:
        cursor.execute("""
            SELECT u.*, uh.goal_type, uh.diet_preference, uh.weight_kg, uh.target_weight,
                   (SELECT bmi_value FROM bmi_records WHERE user_id=u.id ORDER BY recorded_date DESC LIMIT 1) as latest_bmi
            FROM users u
            LEFT JOIN user_health uh ON u.id = uh.user_id
            WHERE u.role='user' AND (u.name LIKE %s OR u.email LIKE %s)
            ORDER BY u.created_at DESC
        """, (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("""
            SELECT u.*, uh.goal_type, uh.diet_preference, uh.weight_kg, uh.target_weight,
                   (SELECT bmi_value FROM bmi_records WHERE user_id=u.id ORDER BY recorded_date DESC LIMIT 1) as latest_bmi
            FROM users u
            LEFT JOIN user_health uh ON u.id = uh.user_id
            WHERE u.role='user'
            ORDER BY u.created_at DESC
        """)

    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/user_management.html', users=users, search=search)


# ================= USER DETAIL =================
@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.user_management'))

    cursor.execute("SELECT * FROM user_health WHERE user_id=%s", (user_id,))
    health = cursor.fetchone()

    cursor.execute("SELECT * FROM bmi_records WHERE user_id=%s ORDER BY recorded_date DESC", (user_id,))
    bmi_records = cursor.fetchall()

    cursor.execute("SELECT * FROM progress_logs WHERE user_id=%s ORDER BY log_date DESC", (user_id,))
    progress = cursor.fetchall()

    cursor.execute("SELECT * FROM goal_predictions WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
    prediction = cursor.fetchone()

    cursor.execute("""
        SELECT al.* FROM activity_logs al 
        WHERE al.user_id=%s ORDER BY al.created_at DESC LIMIT 20
    """, (user_id,))
    user_logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/user_detail.html',
        user=user, health=health, bmi_records=bmi_records,
        progress=progress, prediction=prediction, user_logs=user_logs
    )


# ================= DELETE USER =================
@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s AND role='user'", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(session['user_id'], 'delete_user', f'Deleted user ID: {user_id}')
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin.user_management'))


# ================= MEAL MANAGEMENT =================
@admin_bp.route('/meals')
@admin_required
def meal_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    per_page = 25

    search = request.args.get('search', '').strip()
    filter_type = request.args.get('diet_type', '').strip()
    filter_goal = request.args.get('goal_type', '').strip()

    where_clause = " WHERE 1=1"
    params = []

    if search:
        where_clause += " AND meal_name LIKE %s"
        params.append(f"%{search}%")
    if filter_type:
        where_clause += " AND diet_type=%s"
        params.append(filter_type)
    if filter_goal:
        where_clause += " AND goal_type=%s"
        params.append(filter_goal)

    # Count total records
    count_query = "SELECT COUNT(*) as total FROM diet_meals" + where_clause
    cursor.execute(count_query, tuple(params))
    total_records = cursor.fetchone()['total']

    import math
    total_pages = math.ceil(total_records / per_page) if total_records > 0 else 1
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page

    # Fetch paginated meals
    data_query = "SELECT * FROM diet_meals" + where_clause + " ORDER BY id DESC LIMIT %s OFFSET %s"
    fetch_params = list(params) + [per_page, offset]
    cursor.execute(data_query, tuple(fetch_params))
    meals = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/meal_management.html',
        meals=meals,
        page=page,
        total_pages=total_pages,
        total_records=total_records,
        search=search,
        filter_type=filter_type,
        filter_goal=filter_goal
    )


# ================= ADD/EDIT MEAL =================
@admin_bp.route('/meals/add', methods=['GET', 'POST'])
@admin_bp.route('/meals/<int:meal_id>/edit', methods=['GET', 'POST'])
@admin_required
def meal_form(meal_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    meal = None

    if meal_id:
        cursor.execute("SELECT * FROM diet_meals WHERE id=%s", (meal_id,))
        meal = cursor.fetchone()

    if request.method == 'POST':
        data = {
            'meal_name': request.form['meal_name'],
            'meal_time': request.form['meal_time'],
            'calories': int(request.form['calories']),
            'proteins': float(request.form['proteins']),
            'carbs': float(request.form['carbs']),
            'fats': float(request.form['fats']),
            'diet_type': request.form['diet_type'],
            'goal_type': request.form['goal_type'],
            'option_group': int(request.form['option_group']),
            'img_src': request.form.get('img_src', 'static/images/diet/salad.jpeg')
        }

        if meal_id:
            cursor.execute("""
                UPDATE diet_meals SET meal_name=%s, meal_time=%s, calories=%s,
                proteins=%s, carbs=%s, fats=%s, diet_type=%s, goal_type=%s,
                option_group=%s, img_src=%s WHERE id=%s
            """, (*data.values(), meal_id))
            log_activity(session['user_id'], 'edit_meal', f'Edited meal: {data["meal_name"]}')
        else:
            cursor.execute("""
                INSERT INTO diet_meals (meal_name, meal_time, calories, proteins, carbs, fats,
                diet_type, goal_type, option_group, img_src)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, tuple(data.values()))
            log_activity(session['user_id'], 'add_meal', f'Added meal: {data["meal_name"]}')

        conn.commit()
        cursor.close()
        conn.close()
        flash("Meal saved successfully!", "success")
        return redirect(url_for('admin.meal_management'))

    cursor.close()
    conn.close()
    return render_template('admin/meal_form.html', meal=meal)


# ================= DELETE MEAL =================
@admin_bp.route('/meals/<int:meal_id>/delete', methods=['POST'])
@admin_required
def delete_meal(meal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diet_meals WHERE id=%s", (meal_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(session['user_id'], 'delete_meal', f'Deleted meal ID: {meal_id}')
    flash("Meal deleted.", "success")
    return redirect(url_for('admin.meal_management'))


# ================= WORKOUT MANAGEMENT =================
@admin_bp.route('/workouts')
@admin_required
def workout_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    filter_muscle = request.args.get('muscle', '')
    filter_diff = request.args.get('difficulty', '')

    query = "SELECT * FROM workout_exercises WHERE 1=1"
    params = []

    if filter_muscle:
        query += " AND target_muscle=%s"
        params.append(filter_muscle)
    if filter_diff:
        query += " AND difficulty_level=%s"
        params.append(filter_diff)

    query += " ORDER BY target_muscle, difficulty_level"
    cursor.execute(query, tuple(params))
    exercises = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/workout_management.html', exercises=exercises,
        filter_muscle=filter_muscle, filter_diff=filter_diff)


# ================= ADD/EDIT WORKOUT =================
@admin_bp.route('/workouts/add', methods=['GET', 'POST'])
@admin_bp.route('/workouts/<int:exercise_id>/edit', methods=['GET', 'POST'])
@admin_required
def workout_form(exercise_id=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    exercise = None

    if exercise_id:
        cursor.execute("SELECT * FROM workout_exercises WHERE id=%s", (exercise_id,))
        exercise = cursor.fetchone()

    if request.method == 'POST':
        data = {
            'exercise_name': request.form['exercise_name'],
            'target_muscle': request.form['target_muscle'],
            'muscle_id': int(request.form['muscle_id']),
            'calories_burned': int(request.form['calories_burned']),
            'difficulty_level': request.form['difficulty_level'],
            'option_group': int(request.form['option_group']),
            'img_src': request.form.get('img_src', 'static/images/workout/1.jpg'),
            'video_src': request.form.get('video_src', '')
        }

        if exercise_id:
            cursor.execute("""
                UPDATE workout_exercises SET exercise_name=%s, target_muscle=%s, muscle_id=%s,
                calories_burned=%s, difficulty_level=%s, option_group=%s, img_src=%s, video_src=%s
                WHERE id=%s
            """, (*data.values(), exercise_id))
            log_activity(session['user_id'], 'edit_exercise', f'Edited exercise: {data["exercise_name"]}')
        else:
            cursor.execute("""
                INSERT INTO workout_exercises (exercise_name, target_muscle, muscle_id,
                calories_burned, difficulty_level, option_group, img_src, video_src)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, tuple(data.values()))
            log_activity(session['user_id'], 'add_exercise', f'Added exercise: {data["exercise_name"]}')

        conn.commit()
        cursor.close()
        conn.close()
        flash("Exercise saved successfully!", "success")
        return redirect(url_for('admin.workout_management'))

    cursor.close()
    conn.close()
    return render_template('admin/workout_form.html', exercise=exercise)


# ================= DELETE EXERCISE =================
@admin_bp.route('/workouts/<int:exercise_id>/delete', methods=['POST'])
@admin_required
def delete_exercise(exercise_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workout_exercises WHERE id=%s", (exercise_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(session['user_id'], 'delete_exercise', f'Deleted exercise ID: {exercise_id}')
    flash("Exercise deleted.", "success")
    return redirect(url_for('admin.workout_management'))


# ================= ACTIVITY LOGS =================
@admin_bp.route('/logs')
@admin_required
def activity_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT al.*, u.name as user_name, u.email as user_email
        FROM activity_logs al 
        LEFT JOIN users u ON al.user_id = u.id 
        ORDER BY al.created_at DESC 
        LIMIT 100
    """)
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/activity_logs.html', logs=logs)


# ================= FEEDBACK INBOX =================
@admin_bp.route('/feedback')
@admin_required
def feedback_inbox():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    status_filter = request.args.get('status', '')
    
    query = """
        SELECT uf.*, u.name as user_name, u.email as user_email
        FROM user_feedback uf 
        LEFT JOIN users u ON uf.user_id = u.id
    """
    params = []
    
    if status_filter:
        query += " WHERE uf.status = %s"
        params.append(status_filter)
    
    query += " ORDER BY uf.created_at DESC"
    cursor.execute(query, tuple(params))
    feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/feedback_inbox.html', feedbacks=feedbacks, status_filter=status_filter)


# ================= UPDATE FEEDBACK STATUS =================
@admin_bp.route('/feedback/<int:feedback_id>/update', methods=['POST'])
@admin_required
def update_feedback(feedback_id):
    new_status = request.form.get('status', 'read')
    admin_reply = request.form.get('admin_reply', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_feedback SET status=%s, admin_reply=%s WHERE id=%s",
        (new_status, admin_reply, feedback_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    log_activity(session['user_id'], 'feedback_update', f'Updated feedback #{feedback_id} to {new_status}')
    flash("Feedback updated.", "success")
    return redirect(url_for('admin.feedback_inbox'))


# ================= ADMIN ANALYTICS API =================
@admin_bp.route('/api/stats')
@admin_required
def admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # BMI distribution
    cursor.execute("""
        SELECT bmi_category, COUNT(*) as count FROM (
            SELECT br.bmi_category FROM bmi_records br
            INNER JOIN (
                SELECT user_id, MAX(recorded_date) as latest 
                FROM bmi_records GROUP BY user_id
            ) lb ON br.user_id = lb.user_id AND br.recorded_date = lb.latest
        ) sub GROUP BY bmi_category
    """)
    bmi_dist = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'bmi_distribution': bmi_dist})

# ================= PROFESSIONALS MANAGEMENT =================
@admin_bp.route('/professionals')
@admin_required
def professionals_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM professionals ORDER BY created_at DESC")
    professionals = cursor.fetchall() or []

    verified_count = sum(1 for p in professionals if p.get('is_verified'))
    pending_count = sum(1 for p in professionals if not p.get('is_verified'))

    cursor.close()
    conn.close()

    return render_template('admin/professionals.html',
        professionals=professionals,
        verified_count=verified_count,
        pending_count=pending_count
    )

@admin_bp.route('/professionals/<int:prof_id>/verify', methods=['POST'])
@admin_required
def verify_professional(prof_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE professionals SET is_verified = NOT is_verified WHERE id=%s", (prof_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Professional verification status updated.", "success")
    return redirect(url_for('admin.professionals_management'))

# ================= PAYMENTS =================
@admin_bp.route('/payments')
@admin_required
def payments_view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT p.*, u.name as user_name, pr.full_name as prof_name
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN professionals pr ON p.professional_id = pr.id
        ORDER BY p.created_at DESC
    """)
    payments = cursor.fetchall() or []

    total_commission = round(sum(p['commission_amount'] or 0 for p in payments if p.get('payment_status') == 'paid'), 2)
    total_volume = round(sum(p['amount'] or 0 for p in payments if p.get('payment_status') == 'paid'), 2)
    total_paid_count = sum(1 for p in payments if p.get('payment_status') == 'paid')

    cursor.close()
    conn.close()

    return render_template('admin/payments.html',
        payments=payments,
        total_commission=total_commission,
        total_volume=total_volume,
        total_paid_count=total_paid_count
    )

