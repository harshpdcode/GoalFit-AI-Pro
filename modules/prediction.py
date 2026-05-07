from flask import Blueprint, session, redirect, url_for
from database.db_connection import get_db_connection
from datetime import date, timedelta

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/predict-goal')
def predict_goal():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
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
        return "Health/BMI data missing"

    current_weight = float(health['weight_kg'])
    target_weight = float(health['target_weight'])
    goal_type = health['goal_type']
    bmi_category = bmi_data['bmi_category']

    weight_diff = abs(current_weight - target_weight)

    # Determine weekly rate
    if goal_type == "Weight Loss":
        if bmi_category == "Obese":
            weekly_rate = 1.0
        elif bmi_category == "Overweight":
            weekly_rate = 0.7
        else:
            weekly_rate = 0.4

    elif goal_type == "Weight Gain":
        if bmi_category == "Underweight":
            weekly_rate = 0.6
        else:
            weekly_rate = 0.3

    else:
        return "Maintenance goal — no prediction needed"

    estimated_weeks = round(weight_diff / weekly_rate)

    completion_date = date.today() + timedelta(weeks=estimated_weeks)

    # Save prediction
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

    daily_calorie_burn = total_calories / (estimated_weeks * 7)

    walking_calories = daily_calorie_burn * 0.4

    steps_per_day = int(walking_calories / 0.04)

    # Cap realistic limits
    if goal_type == "Weight Loss":
        steps_per_day = min(max(steps_per_day, 8000), 12000)

    elif goal_type == "Weight Gain":
        steps_per_day = min(max(steps_per_day, 5000), 8000)

    else:
        steps_per_day = 7000

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
    conn.close()

    return f"""
    Goal Prediction Complete <br>
    Weeks Required: {estimated_weeks} <br>
    Completion Date: {completion_date} <br>
    Daily Steps Needed: {steps_per_day}
    """