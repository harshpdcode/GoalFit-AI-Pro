from flask import Blueprint, session, redirect, url_for
from database.db_connection import get_db_connection
from datetime import date

bmi_bp = Blueprint('bmi', __name__)

@bmi_bp.route('/calculate-bmi')
def calculate_bmi():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute(
        "SELECT height_cm, weight_kg FROM user_health WHERE user_id=%s",
        (user_id,)
    )
    data = cursor.fetchone()

    if not data:
        return "Health data not found"

    height = float(data['height_cm'])
    weight = float(data['weight_kg'])

    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    cursor.execute("""
        INSERT INTO bmi_records
        (user_id, bmi_value, bmi_category, recorded_date)
        VALUES (%s, %s, %s, %s)
    """, (user_id, round(bmi,2), category, date.today()))

    conn.commit()
    cursor.close()
    conn.close()

    return f"Your BMI is {round(bmi,2)} ({category})"