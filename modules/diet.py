from flask import Blueprint, session, redirect, url_for, render_template
from database.db_connection import get_db_connection

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/diet-plan')
def diet_plan():

    # ---------- SESSION CHECK ----------
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    try:
        # ---------- FETCH USER HEALTH ----------
        cursor.execute("""
            SELECT goal_type, diet_preference
            FROM user_health
            WHERE user_id = %s
        """, (user_id,))
        health = cursor.fetchone()

        if not health:
            return redirect(url_for('health.health_profile'))

        goal = health['goal_type'].strip()
        diet_pref = health['diet_preference'].strip()

        # ---------- FETCH MEALS ----------
        cursor.execute("""
            SELECT *
            FROM diet_meals
            WHERE goal_type = %s
            AND diet_type = %s
            ORDER BY meal_time, option_group
        """, (goal, diet_pref))

        all_meals = cursor.fetchall()

        # ---------- HARD FALLBACK ----------
        if not all_meals:
            cursor.execute("""
                SELECT *
                FROM diet_meals
                ORDER BY meal_time, option_group
            """)
            all_meals = cursor.fetchall()

        # ---------- STRICT GROUPING ----------
        grouped_meals = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snacks": []
        }

        for meal in all_meals:
            meal_time = (meal.get("meal_time") or "").strip().lower()

            if meal_time == "breakfast":
                grouped_meals["breakfast"].append(meal)

            elif meal_time == "lunch":
                grouped_meals["lunch"].append(meal)

            elif meal_time == "dinner":
                grouped_meals["dinner"].append(meal)

            elif meal_time == "snacks":
                grouped_meals["snacks"].append(meal)

        return render_template(
            "diet/diet_plan.html",
            meals=grouped_meals,
            goal=goal,
            bmi="Based on your profile",
            diet_pref=diet_pref,
            user_name=session.get('user_name'),
            email=session.get('email')
        )

    finally:
        cursor.close()
        conn.close()