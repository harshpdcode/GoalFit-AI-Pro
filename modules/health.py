from flask import Blueprint, render_template, request, session, redirect, url_for
from database.db_connection import get_db_connection
from datetime import date, timedelta

health_bp = Blueprint('health', __name__)

def save_initial_bmi_and_progress(user_id, weight_kg, height_cm, conn):
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        h_m = float(height_cm) / 100.0
        w_kg = float(weight_kg)
        bmi_val = round(w_kg / (h_m ** 2), 1) if h_m > 0 else 22.0
        
        if bmi_val < 18.5:
            cat = "Underweight"
        elif bmi_val < 25.0:
            cat = "Normal"
        elif bmi_val < 30.0:
            cat = "Overweight"
        else:
            cat = "Obese"
            
        today_date = date.today()
        
        # Save BMI record
        cursor.execute("DELETE FROM bmi_records WHERE user_id=%s AND recorded_date=%s", (user_id, today_date))
        cursor.execute("""
            INSERT INTO bmi_records (user_id, bmi_value, bmi_category, recorded_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, bmi_val, cat, today_date))
        
        # Save Progress log if no logs yet
        cursor.execute("SELECT COUNT(*) as count FROM progress_logs WHERE user_id=%s", (user_id,))
        cnt = cursor.fetchone()['count']
        if cnt == 0:
            cursor.execute("""
                INSERT INTO progress_logs (user_id, weight_kg, log_date)
                VALUES (%s, %s, %s)
            """, (user_id, w_kg, today_date))
        conn.commit()
    except Exception as e:
        print(f"Error in save_initial_bmi_and_progress: {e}")
    finally:
        cursor.close()


def calculate_and_save_prediction(user_id, conn):
    """Calculate and save goal prediction and step recommendations"""
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Get health data
    cursor.execute("""
        SELECT weight_kg, target_weight, goal_type
        FROM user_health
        WHERE user_id=%s
    """, (user_id,))
    health = cursor.fetchone()

    # Get latest BMI category
    cursor.execute("""
        SELECT bmi_category
        FROM bmi_records
        WHERE user_id=%s
        ORDER BY recorded_date DESC
        LIMIT 1
    """, (user_id,))
    bmi_data = cursor.fetchone()

    if not health or not bmi_data:
        cursor.close()
        return

    current_weight = float(health['weight_kg'])
    target_weight = float(health['target_weight'])
    goal_type = health['goal_type']
    bmi_category = bmi_data['bmi_category']

    weight_diff = abs(current_weight - target_weight)

    # Determine weekly rate
    lt = goal_type.lower()
    if "loss" in lt:
        # treat any loss-like goal as weight loss
        if bmi_category == "Obese":
            weekly_rate = 1.0
        elif bmi_category == "Overweight":
            weekly_rate = 0.7
        else:
            weekly_rate = 0.4

    elif "gain" in lt:
        # any gain-like goal as weight gain
        if bmi_category == "Underweight":
            weekly_rate = 0.6
        else:
            weekly_rate = 0.3

    else:
        # maintenance or unknown
        cursor.close()
        return

    estimated_weeks = max(1, round(weight_diff / weekly_rate)) if weekly_rate > 0 else 1

    completion_date = date.today() + timedelta(weeks=estimated_weeks)

    # Clear old predictions and insert new one
    cursor.execute("DELETE FROM goal_predictions WHERE user_id=%s", (user_id,))
    
    cursor.execute("""
        INSERT INTO goal_predictions
        (user_id, current_weight, target_weight,
         weekly_change_rate, estimated_weeks,
         estimated_completion_date)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        user_id,
        current_weight,
        target_weight,
        weekly_rate,
        estimated_weeks,
        completion_date
    ))

    # Step estimation logic
    calories_per_kg = 7700
    total_calories = weight_diff * calories_per_kg
    daily_calorie_burn = total_calories / (estimated_weeks * 7) if estimated_weeks > 0 else 500
    walking_calories = daily_calorie_burn * 0.4
    steps_per_day = int(walking_calories / 0.04) if walking_calories > 0 else 7000

    # Cap realistic limits
    if goal_type == "Weight Loss":
        steps_per_day = min(max(steps_per_day, 8000), 12000)
    elif goal_type == "Weight Gain":
        steps_per_day = min(max(steps_per_day, 5000), 8000)
    else:
        steps_per_day = 7000

    cursor.execute("DELETE FROM step_recommendations WHERE user_id=%s", (user_id,))
    
    cursor.execute("""
        INSERT INTO step_recommendations
        (user_id, daily_steps, calories_to_burn, distance_km)
        VALUES (%s,%s,%s,%s)
    """, (
        user_id,
        steps_per_day,
        int(daily_calorie_burn),
        round(steps_per_day * 0.0008, 2)
    ))

    conn.commit()
    cursor.close()


@health_bp.route('/health', methods=['GET', 'POST'])
def health_profile():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Fetch existing profile
    cursor.execute("""
        SELECT * FROM user_health
        WHERE user_id=%s
    """, (user_id,))
    health = cursor.fetchone()

    if request.method == 'POST':

        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        activity = request.form['activity_level']
        goal = request.form['goal_type']
        target = request.form['target_weight']
        diet = request.form['diet_preference']

        if health:
            # UPDATE existing profile
            cursor.execute("""
                UPDATE user_health
                SET age=%s, gender=%s, height_cm=%s, weight_kg=%s,
                    activity_level=%s, goal_type=%s,
                    target_weight=%s, diet_preference=%s
                WHERE user_id=%s
            """, (age, gender, height, weight,
                  activity, goal, target, diet, user_id))
        else:
            # INSERT new profile
            cursor.execute("""
                INSERT INTO user_health
                (user_id, age, gender, height_cm, weight_kg,
                 activity_level, goal_type, target_weight, diet_preference)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, age, gender, height, weight,
                  activity, goal, target, diet))

        conn.commit()

        # Save initial BMI record and progress log for new users
        save_initial_bmi_and_progress(user_id, weight, height, conn)

        # Reset saved user meal selections so diet plan regenerates dynamically for new preferences
        try:
            cursor.execute("DELETE FROM user_selected_meals WHERE user_id=%s", (user_id,))
        except Exception:
            pass

        # Calculate predictions after saving health data
        calculate_and_save_prediction(user_id, conn)

        # Clear first-time login flag
        session.pop('first_time_login', None)

        cursor.close()
        conn.close()

        return redirect(url_for('dashboard.dashboard'))

    cursor.close()
    conn.close()

    return render_template(
        'user/health_form.html',
        health=health,
        user_name=session.get('user_name'),
        email=session.get('email'),
        session=session
    )
