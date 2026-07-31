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

    # Calculate Ideal Weight Range (BMI 18.5 to 24.9)
    h_m = float(health['height_cm']) / 100.0
    health['ideal_weight_min'] = round(18.5 * (h_m ** 2), 1)
    health['ideal_weight_max'] = round(24.9 * (h_m ** 2), 1)

    # ---------- BMI ----------
    cursor.execute("""
        SELECT bmi_value, bmi_category
        FROM bmi_records
        WHERE user_id=%s
        ORDER BY recorded_date DESC
        LIMIT 1
    """, (user_id,))
    bmi = cursor.fetchone()

    if not bmi or bmi.get('bmi_value') == "--":
        try:
            h_m = float(health['height_cm']) / 100.0
            w_kg = float(health['weight_kg'])
            calc_bmi = round(w_kg / (h_m ** 2), 1) if h_m > 0 else 22.0
            cat = "Normal"
            if calc_bmi < 18.5: cat = "Underweight"
            elif calc_bmi >= 25.0 and calc_bmi < 30.0: cat = "Overweight"
            elif calc_bmi >= 30.0: cat = "Obese"
            bmi = {"bmi_value": calc_bmi, "bmi_category": cat}
        except Exception:
            bmi = {"bmi_value": 22.5, "bmi_category": "Normal"}
        
    bmi['ideal_weight_min'] = health['ideal_weight_min']
    bmi['ideal_weight_max'] = health['ideal_weight_max']

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
            from modules.health import save_initial_bmi_and_progress, calculate_and_save_prediction
            save_initial_bmi_and_progress(user_id, health['weight_kg'], health['height_cm'], conn)
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

    if not prediction:
        from datetime import date, timedelta
        prediction = {
            "estimated_weeks": 8,
            "weekly_change_rate": 0.5,
            "estimated_completion_date": date.today() + timedelta(weeks=8)
        }

    # ---------- STEPS ----------
    cursor.execute("""
        SELECT daily_steps, calories_to_burn
        FROM step_recommendations
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))
    steps = cursor.fetchone()
    
    if not steps or steps.get("daily_steps", 0) == 0:
        goal_l = (health.get('goal_type') or '').lower()
        if "loss" in goal_l:
            st, cal = 10000, 400
        elif "gain" in goal_l:
            st, cal = 6500, 250
        else:
            st, cal = 8000, 320
        steps = {"daily_steps": st, "calories_to_burn": cal}

    # ---------- PROGRESS OVERVIEW STATS ----------
    cursor.execute("""
        SELECT weight_kg, log_date
        FROM progress_logs
        WHERE user_id=%s
        ORDER BY log_date ASC
    """, (user_id,))
    p_logs = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT log_date
        FROM progress_logs
        WHERE user_id=%s
        ORDER BY log_date DESC
    """, (user_id,))
    log_dates = [row['log_date'] for row in cursor.fetchall()]

    streak = 0
    if log_dates:
        from datetime import date, timedelta
        today = date.today()
        if log_dates[0] == today or log_dates[0] == today - timedelta(days=1):
            streak = 1
            curr = log_dates[0]
            for d in log_dates[1:]:
                if d == curr - timedelta(days=1):
                    streak += 1
                    curr = d
                else:
                    break
        else:
            streak = 1
    else:
        streak = 1

    start_w = p_logs[0]['weight_kg'] if p_logs else health['weight_kg']
    latest_w = p_logs[-1]['weight_kg'] if p_logs else health['weight_kg']
    target_w = float(health['target_weight']) if health.get('target_weight') else start_w

    if target_w < start_w:
        t_diff = start_w - target_w
        d_diff = start_w - latest_w
        raw_pct = (d_diff / t_diff) * 100 if t_diff > 0 else 100.0
    elif target_w > start_w:
        t_diff = target_w - start_w
        d_diff = latest_w - start_w
        raw_pct = (d_diff / t_diff) * 100 if t_diff > 0 else 100.0
    else:
        raw_pct = 100.0

    goal_progress_pct = round(max(0.0, min(100.0, raw_pct)), 1)
    weight_changed = round(abs(latest_w - start_w), 1)
    is_weight_loss = target_w <= start_w

    overview_stats = {
        "streak": streak,
        "goal_progress_pct": goal_progress_pct,
        "weight_changed": weight_changed,
        "is_weight_loss": is_weight_loss
    }

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
        workout=workout,
        overview_stats=overview_stats
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

    if not weights:
        cursor.execute("SELECT weight_kg FROM user_health WHERE user_id=%s", (user_id,))
        h = cursor.fetchone()
        if h and h.get('weight_kg'):
            from datetime import date
            weights = [{"weight_kg": h['weight_kg'], "log_date": str(date.today())}]

    if not bmi:
        cursor.execute("SELECT height_cm, weight_kg FROM user_health WHERE user_id=%s", (user_id,))
        h = cursor.fetchone()
        if h and h.get('weight_kg') and h.get('height_cm'):
            from datetime import date
            h_m = float(h['height_cm']) / 100.0
            calc_b = round(float(h['weight_kg']) / (h_m ** 2), 1) if h_m > 0 else 22.0
            bmi = [{"bmi_value": calc_b, "recorded_date": str(date.today())}]

    cursor.close()
    conn.close()

    return jsonify({
        "weights": weights,
        "bmi": bmi
    })