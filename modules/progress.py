from flask import Blueprint, render_template, request, session, redirect, url_for
from database.db_connection import get_db_connection
from datetime import date

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/progress', methods=['GET', 'POST'])
def progress():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Insert new weight and recalculate everything
    if request.method == 'POST':
        weight = float(request.form['weight'])

        # 1. Add progress
        cursor.execute("INSERT INTO progress_logs (user_id, weight_kg, log_date) VALUES (%s, %s, %s)", (user_id, weight, date.today()))

        # 2. Update health table
        cursor.execute("UPDATE user_health SET weight_kg=%s WHERE user_id=%s", (weight, user_id))

        # 3. Recalculate BMI
        cursor.execute("SELECT height_cm, target_weight, goal_type FROM user_health WHERE user_id=%s", (user_id,))
        h_data = cursor.fetchone()
        
        if h_data and h_data['height_cm']:
            h_m = float(h_data['height_cm']) / 100.0
            bmi_val = round(weight / (h_m * h_m), 1)
            
            if bmi_val < 18.5: cat = "Underweight"
            elif bmi_val < 25: cat = "Normal"
            elif bmi_val < 30: cat = "Overweight"
            else: cat = "Obese"
            
            cursor.execute("INSERT INTO bmi_records (user_id, bmi_value, bmi_category, recorded_date) VALUES (%s, %s, %s, %s)", (user_id, bmi_val, cat, date.today()))
            
            # 4. Recalculate Prediction & Steps
            tw = float(h_data['target_weight'])
            g_type = h_data['goal_type']
            w_diff = abs(weight - tw)
            
            rate = 0.5
            if g_type == "Weight Loss": rate = 0.8
            elif g_type == "Weight Gain": rate = 0.5
            
            if w_diff > 0.5:
                est_wks = max(int(w_diff / rate), 1)
                from datetime import timedelta
                comp_date = date.today() + timedelta(weeks=est_wks)
                
                # Predict goals Update
                cursor.execute("DELETE FROM goal_predictions WHERE user_id=%s", (user_id,))
                cursor.execute("""
                    INSERT INTO goal_predictions (user_id, current_weight, target_weight, weekly_change_rate, estimated_weeks, estimated_completion_date) 
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (user_id, weight, tw, rate, est_wks, comp_date))
                
                # Steps Update
                total_cals = w_diff * 7700
                daily_cals = total_cals / (est_wks * 7)
                steps = int((daily_cals * 0.4) / 0.04)
                
                if g_type == "Weight Loss": steps = min(max(steps, 8000), 12000)
                else: steps = min(max(steps, 5000), 8000)
                
                cursor.execute("DELETE FROM step_recommendations WHERE user_id=%s", (user_id,))
                cursor.execute("""
                    INSERT INTO step_recommendations (user_id, daily_steps, calories_to_burn, distance_km) 
                    VALUES (%s,%s,%s,%s)
                """, (user_id, steps, int(daily_cals), round(steps * 0.0008, 2)))

        conn.commit()
        return redirect(url_for('progress.progress'))

    # Fetch weight history
    cursor.execute("""
        SELECT weight_kg, log_date
        FROM progress_logs
        WHERE user_id=%s
        ORDER BY log_date ASC
    """, (user_id,))

    logs = cursor.fetchall()

    # Fetch BMI data
    cursor.execute("""
        SELECT bmi_value, recorded_date
        FROM bmi_records
        WHERE user_id=%s
        ORDER BY recorded_date ASC
    """, (user_id,))

    bmi_logs = cursor.fetchall()

    # Fetch health data
    cursor.execute("""
        SELECT weight_kg, target_weight
        FROM user_health
        WHERE user_id=%s
    """, (user_id,))

    health = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'user/progress.html',
        logs=logs,
        bmi_logs=bmi_logs,
        health=health,
        user_name=session.get('user_name'),
        email=session.get('email')
    )