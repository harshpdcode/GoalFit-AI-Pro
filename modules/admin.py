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


# ================= ADMIN DASHBOARD =================
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Total users
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='user'")
    total_users = cursor.fetchone()['total']

    # New users this week
    cursor.execute("""
        SELECT COUNT(*) as new_week FROM users 
        WHERE role='user' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """)
    new_this_week = cursor.fetchone()['new_week']

    # Total professionals
    cursor.execute("SELECT COUNT(*) as total FROM professionals")
    total_professionals = cursor.fetchone()['total']

    # Total revenue
    cursor.execute("SELECT SUM(commission_amount) as rev FROM payments WHERE payment_status='paid'")
    total_revenue = cursor.fetchone()['rev'] or 0

    # Total hire requests
    cursor.execute("SELECT COUNT(*) as total FROM hire_requests")
    total_hire_requests = cursor.fetchone()['total']

    # Average BMI
    cursor.execute("""
        SELECT ROUND(AVG(bmi_value), 1) as avg_bmi 
        FROM bmi_records br
        INNER JOIN (
            SELECT user_id, MAX(recorded_date) as latest 
            FROM bmi_records GROUP BY user_id
        ) latest_bmi ON br.user_id = latest_bmi.user_id AND br.recorded_date = latest_bmi.latest
    """)
    avg_bmi_row = cursor.fetchone()
    avg_bmi = avg_bmi_row['avg_bmi'] if avg_bmi_row['avg_bmi'] else 0

    # Total meals & exercises
    cursor.execute("SELECT COUNT(*) as total FROM diet_meals")
    total_meals = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM workout_exercises")
    total_exercises = cursor.fetchone()['total']

    # Unread feedback
    cursor.execute("SELECT COUNT(*) as unread FROM user_feedback WHERE status='unread'")
    unread_feedback = cursor.fetchone()['unread']

    # Goal type distribution
    cursor.execute("""
        SELECT goal_type, COUNT(*) as count FROM user_health 
        GROUP BY goal_type
    """)
    goal_dist = cursor.fetchall()

    # Diet preference distribution
    cursor.execute("""
        SELECT diet_preference, COUNT(*) as count FROM user_health 
        GROUP BY diet_preference
    """)
    diet_dist = cursor.fetchall()

    # Recent activity logs
    cursor.execute("""
        SELECT al.*, u.name as user_name 
        FROM activity_logs al 
        LEFT JOIN users u ON al.user_id = u.id 
        ORDER BY al.created_at DESC LIMIT 10
    """)
    recent_logs = cursor.fetchall()

    # User growth (last 30 days)
    cursor.execute("""
        SELECT DATE(created_at) as reg_date, COUNT(*) as count 
        FROM users WHERE role='user'
        GROUP BY DATE(created_at) 
        ORDER BY reg_date DESC LIMIT 30
    """)
    user_growth = cursor.fetchall()

    # Payment growth (last 30 days)
    cursor.execute("""
        SELECT DATE(created_at) as pay_date, SUM(commission_amount) as daily_revenue 
        FROM payments WHERE payment_status='paid' AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(created_at) 
        ORDER BY pay_date ASC
    """)
    payment_growth = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/admin_dashboard.html',
        total_users=total_users,
        new_this_week=new_this_week,
        total_professionals=total_professionals,
        total_revenue=total_revenue,
        total_hire_requests=total_hire_requests,
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

    filter_type = request.args.get('diet_type', '')
    filter_goal = request.args.get('goal_type', '')

    query = "SELECT * FROM diet_meals WHERE 1=1"
    params = []

    if filter_type:
        query += " AND diet_type=%s"
        params.append(filter_type)
    if filter_goal:
        query += " AND goal_type=%s"
        params.append(filter_goal)

    query += " ORDER BY meal_time, diet_type, goal_type"
    cursor.execute(query, tuple(params))
    meals = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/meal_management.html', meals=meals,
        filter_type=filter_type, filter_goal=filter_goal)


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
    professionals = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/professionals.html', professionals=professionals)

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
        JOIN users u ON p.user_id = u.id
        JOIN professionals pr ON p.professional_id = pr.id
        ORDER BY p.created_at DESC
    """)
    payments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/payments.html', payments=payments)

