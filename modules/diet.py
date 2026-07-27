from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from database.db_connection import get_db_connection

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/diet/select-meal', methods=['POST'])
def select_active_meal():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json() if request.is_json else request.form
    meal_id = data.get('meal_id')
    category = (data.get('category') or '').strip().lower()

    if not meal_id or not category:
        return jsonify({'success': False, 'message': 'Invalid parameters'}), 400

    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database error'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_selected_meals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                meal_category VARCHAR(50),
                meal_id INT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (meal_id) REFERENCES diet_meals(id) ON DELETE CASCADE,
                UNIQUE KEY user_category_uniq (user_id, meal_category)
            );
        """)
        cursor.execute("""
            INSERT INTO user_selected_meals (user_id, meal_category, meal_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE meal_id = VALUES(meal_id)
        """, (user_id, category, meal_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        if request.is_json:
            return jsonify({'success': True, 'message': f'Active {category} meal updated!'})
        return redirect(url_for('diet.diet_plan'))
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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

        goal = (health.get('goal_type') or 'Weight Loss').strip()
        diet_pref = (health.get('diet_preference') or 'Vegetarian').strip()

        # Normalize diet preference for database lookup
        norm_diet_pref = 'Veg'
        if 'non' in diet_pref.lower():
            norm_diet_pref = 'Non-Veg'
        elif 'vegan' in diet_pref.lower():
            norm_diet_pref = 'Vegan'
        elif 'egg' in diet_pref.lower():
            norm_diet_pref = 'Eggetarian'
        elif 'keto' in diet_pref.lower():
            norm_diet_pref = 'Keto'
        elif 'veg' in diet_pref.lower():
            norm_diet_pref = 'Veg'

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

        # ---------- FETCH ACTIVE USER SELECTED MEALS ----------
        user_selected_map = {}
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_selected_meals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    meal_category VARCHAR(50),
                    meal_id INT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (meal_id) REFERENCES diet_meals(id) ON DELETE CASCADE,
                    UNIQUE KEY user_category_uniq (user_id, meal_category)
                );
            """)
            cursor.execute("SELECT meal_category, meal_id FROM user_selected_meals WHERE user_id = %s", (user_id,))
            user_selected_rows = cursor.fetchall()
            user_selected_map = {row['meal_category'].lower(): row['meal_id'] for row in user_selected_rows}
        except Exception as e:
            print(f"User selected meals query fallback: {e}")

        # ---------- FETCH MEAL OPTIONS PER CATEGORY ----------
        categories = ['breakfast', 'lunch', 'dinner', 'snacks']
        grouped_options = {c: [] for c in categories}
        active_meals = {}

        for cat in categories:
            db_cat_search = 'Breakfast' if cat == 'breakfast' else ('Lunch' if cat == 'lunch' else ('Dinner' if cat == 'dinner' else 'Snack'))
            
            cursor.execute("""
                SELECT * FROM diet_meals
                WHERE (diet_type = %s OR diet_type = %s)
                  AND (goal_type = %s OR goal_type LIKE %s)
                  AND (meal_time = %s OR meal_time LIKE %s)
                ORDER BY calories ASC
                LIMIT 50
            """, (norm_diet_pref, diet_pref, goal, f"%{goal}%", db_cat_search, f"%{db_cat_search}%"))
            
            options = cursor.fetchall()

            # Fallback if specific category was empty
            if not options:
                cursor.execute("""
                    SELECT * FROM diet_meals
                    WHERE (meal_time = %s OR meal_time LIKE %s)
                    ORDER BY calories ASC
                    LIMIT 20
                """, (db_cat_search, f"%{db_cat_search}%"))
                options = cursor.fetchall()

            grouped_options[cat] = options

            # Determine Active Meal
            selected_meal_id = user_selected_map.get(cat)
            active_m = None

            if selected_meal_id:
                for opt in options:
                    if opt['id'] == selected_meal_id:
                        active_m = opt
                        break
                if not active_m:
                    cursor.execute("SELECT * FROM diet_meals WHERE id = %s", (selected_meal_id,))
                    active_m = cursor.fetchone()
                
                # Verify active_m matches current diet preference
                if active_m:
                    m_diet = (active_m.get('diet_type') or '').lower()
                    if norm_diet_pref.lower() not in m_diet and m_diet not in diet_pref.lower():
                        active_m = None

            if not active_m and options:
                active_m = options[0]
                try:
                    cursor.execute("""
                        INSERT INTO user_selected_meals (user_id, meal_category, meal_id)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE meal_id = VALUES(meal_id)
                    """, (user_id, cat, active_m['id']))
                except Exception:
                    pass

            active_meals[cat] = active_m

        # Fetch today's logs for checklist
        from datetime import datetime
        today = datetime.now().date()
        cursor.execute("SELECT meal_id, is_completed FROM diet_logs WHERE user_id=%s AND log_date=%s", (user_id, today))
        logs = cursor.fetchall()
        diet_logs = {log['meal_id']: log['is_completed'] for log in logs}

        return render_template(
            "diet/diet_plan.html",
            active_meals=active_meals,
            grouped_options=grouped_options,
            goal=goal,
            bmi="Based on your profile",
            diet_pref=diet_pref,
            tdee_data=tdee_data,
            diet_logs=diet_logs,
            log_date=today,
            user_name=session.get('user_name'),
            email=session.get('email')
        )

    finally:
        cursor.close()
        conn.close()