from flask import Blueprint, session, redirect, url_for, render_template, jsonify
from database.db_connection import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)


# ================= DASHBOARD =================
@dashboard_bp.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # ---------- HEALTH ----------
    cursor.execute("""
        SELECT *
        FROM user_health
        WHERE user_id=%s
    """, (user_id,))
    health = cursor.fetchone()

    if not health:
        cursor.close()
        conn.close()
        return redirect(url_for('health.health_profile'))

    # Calculate BMR (Mifflin-St Jeor)
    if health['gender'] == 'Male':
        health['bmr'] = round((10 * health['weight_kg']) + (6.25 * health['height_cm']) - (5 * health['age']) + 5)
    else:
        health['bmr'] = round((10 * health['weight_kg']) + (6.25 * health['height_cm']) - (5 * health['age']) - 161)


    # ---------- BMI ----------
    cursor.execute("""
        SELECT bmi_value, bmi_category
        FROM bmi_records
        WHERE user_id=%s
        ORDER BY recorded_date DESC
        LIMIT 1
    """, (user_id,))
    bmi = cursor.fetchone()

    # ---------- GOAL PREDICTION ----------
    cursor.execute("""
        SELECT estimated_weeks,
               weekly_change_rate,
               estimated_completion_date
        FROM goal_predictions
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    prediction = cursor.fetchone()

    # if no prediction yet, generate one now
    if not prediction:
        try:
            from modules.health import calculate_and_save_prediction
            calculate_and_save_prediction(user_id, conn)
        except Exception as e:
            print(f"Error generating prediction on dashboard: {e}")
        cursor.execute("""
            SELECT estimated_weeks,
                   weekly_change_rate,
                   estimated_completion_date
            FROM goal_predictions
            WHERE user_id=%s
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))
        prediction = cursor.fetchone()

    # ---------- STEPS ----------
    cursor.execute("""
        SELECT daily_steps, calories_to_burn
        FROM step_recommendations
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    steps = cursor.fetchone()
    
    if not steps:
        steps = {"daily_steps": 0, "calories_to_burn": 0}
        
    if not bmi:
        bmi = {"bmi_value": "--", "bmi_category": "No Record"}

    # ---------- MEALS ----------
    cursor.execute("""
        SELECT COUNT(*) as total_meals
        FROM diet_meals
    """)
    meal_counts = cursor.fetchone()

    # ---------- WORKOUTS ----------
    cursor.execute("""
        SELECT COUNT(*) as total_exercises
        FROM workout_exercises
    """)
    workout = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        user_name=session.get('user_name'),
        email=session.get('email'),
        health=health,
        bmi=bmi,
        prediction=prediction,
        steps=steps,
        meal_counts=meal_counts,
        workout=workout
    )


# ================= PROGRESS API =================
@dashboard_bp.route('/dashboard-progress-data')
def dashboard_progress_data():

    if 'user_id' not in session:
        return jsonify({})

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT weight_kg, log_date
        FROM progress_logs
        WHERE user_id=%s
        ORDER BY log_date
    """, (user_id,))
    weights = cursor.fetchall()

    cursor.execute("""
        SELECT bmi_value, recorded_date
        FROM bmi_records
        WHERE user_id=%s
        ORDER BY recorded_date
    """, (user_id,))
    bmi = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "weights": weights,
        "bmi": bmi
    })