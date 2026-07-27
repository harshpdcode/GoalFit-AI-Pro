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

    # CHECK IF HIRED A DIETICIAN
    cursor.execute("""
        SELECT ca.*, p.full_name as prof_name, p.role
        FROM client_assignments ca
        JOIN professionals p ON ca.professional_id = p.id
        WHERE ca.user_id=%s AND ca.status='active' AND p.role IN ('dietician', 'both')
    """, (user_id,))
    active_dietician = cursor.fetchone()

    if active_dietician:
        # Load custom plans from custom_diet_plans / custom_diet_plan_meals
        cursor.execute("SELECT * FROM custom_diet_plans WHERE user_id=%s AND professional_id=%s ORDER BY created_at DESC LIMIT 1", (user_id, active_dietician['professional_id']))
        custom_plan = cursor.fetchone()
        custom_meals = []
        if custom_plan:
            cursor.execute("""
                SELECT c.meal_type, c.meal_id, m.meal_name, m.calories, m.protein, m.carbs, m.fats, m.ingredients, m.instructions, m.image as img_src
                FROM custom_diet_plan_meals c
                JOIN professional_meals m ON c.meal_id = m.id
                WHERE c.plan_id=%s
            """, (custom_plan['id'],))
            custom_meals = cursor.fetchall()
            
        # Fetch today's diet logs
        from datetime import datetime
        today = datetime.now().date()
        cursor.execute("SELECT meal_id, is_completed FROM diet_logs WHERE user_id=%s AND log_date=%s", (user_id, today))
        logs = cursor.fetchall()
        diet_logs = {log['meal_id']: log['is_completed'] for log in logs}
            
        return render_template('diet/diet_plan.html', 
                               coach=active_dietician,
                               custom_plan=custom_plan,
                               custom_meals=custom_meals,
                               diet_logs=diet_logs,
                               log_date=today,
                               user_name=session.get('user_name'),
                               current_role=session.get('role', 'user'))

    try:
        # ---------- FETCH USER HEALTH ----------
        cursor.execute("""
            SELECT *
            FROM user_health
            WHERE user_id = %s
        """, (user_id,))
        health = cursor.fetchone()

        if not health:
            return redirect(url_for('health.health_profile'))

        goal = health['goal_type'].strip()
        diet_pref = health['diet_preference'].strip()

        # ---------- CALCULATE TDEE & MACROS ----------
        w = float(health.get('weight_kg', 70))
        h = float(health.get('height_cm', 170))
        age = int(health.get('age', 25))
        gender = health.get('gender', 'Male')
        act_str = str(health.get('activity_level', 'Moderately Active')).lower()

        if gender == 'Male':
            bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
        else:
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161

        act_mult = 1.55
        if 'sedentary' in act_str: act_mult = 1.2
        elif 'light' in act_str: act_mult = 1.375
        elif 'very' in act_str: act_mult = 1.725
        elif 'extra' in act_str or 'extreme' in act_str: act_mult = 1.9

        tdee = round(bmr * act_mult)
        target_calories = tdee
        goal_lower = goal.lower()
        if 'loss' in goal_lower:
            target_calories = tdee - 500
        elif 'gain' in goal_lower:
            target_calories = tdee + 400

        protein_g = round((target_calories * 0.25) / 4)
        carbs_g = round((target_calories * 0.50) / 4)
        fats_g = round((target_calories * 0.25) / 9)

        tdee_data = {
            'bmr': round(bmr),
            'tdee': tdee,
            'target_calories': target_calories,
            'protein_g': protein_g,
            'carbs_g': carbs_g,
            'fats_g': fats_g,
            'activity': health.get('activity_level', 'Moderately Active'),
            'goal': goal
        }

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

            elif "snack" in meal_time:
                grouped_meals["snacks"].append(meal)

        return render_template(
            "diet/diet_plan.html",
            meals=grouped_meals,
            goal=goal,
            bmi="Based on your profile",
            diet_pref=diet_pref,
            tdee_data=tdee_data,
            user_name=session.get('user_name'),
            email=session.get('email')
        )

    finally:
        cursor.close()
        conn.close()