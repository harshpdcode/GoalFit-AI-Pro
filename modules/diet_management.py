from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.professional_dashboard import pro_required, get_db_connection

pro_diet_bp = Blueprint('pro_diet_bp', __name__, url_prefix='/pro/diet')

@pro_diet_bp.route('/library')
@pro_required
def library():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM professional_meals WHERE professional_id = %s ORDER BY id DESC", (prof_id,))
    meals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('professional/diet_library.html', meals=meals)

@pro_diet_bp.route('/meal/create', methods=['GET', 'POST'])
@pro_required
def create_meal():
    if request.method == 'POST':
        prof_id = session.get('user_id')
        meal_name = request.form.get('meal_name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        carbs = request.form.get('carbs')
        fats = request.form.get('fats')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        
        # Image upload handling could be added here
        img_src = 'static/images/diet/default_meal.jpg'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO professional_meals (professional_id, meal_name, calories, protein, carbs, fats, ingredients, instructions, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (prof_id, meal_name, calories, protein, carbs, fats, ingredients, instructions, img_src))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Meal added to library successfully!", "success")
        return redirect(url_for('pro_diet_bp.library'))
        
    return render_template('professional/diet_create.html')

@pro_diet_bp.route('/plan/create', methods=['GET', 'POST'])
@pro_required
def create_plan():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get active clients for this professional
    cursor.execute("""
        SELECT ca.user_id, u.name 
        FROM client_assignments ca
        JOIN users u ON ca.user_id = u.id
        WHERE ca.professional_id = %s AND ca.status = 'active'
    """, (prof_id,))
    clients = cursor.fetchall()
    
    # Get professional's meal library
    cursor.execute("SELECT * FROM professional_meals WHERE professional_id = %s", (prof_id,))
    meals = cursor.fetchall()
    
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        plan_name = request.form.get('plan_name')
        goal = request.form.get('goal')
        notes = request.form.get('notes')
        
        # Insert main plan
        cursor.execute("""
            INSERT INTO custom_diet_plans (user_id, professional_id, plan_name, goal, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_id, prof_id, plan_name, goal, notes))
        plan_id = cursor.lastrowid
        
        # Insert selected meals
        # The form should send meal IDs as arrays named by meal_type, e.g. meal_breakfast[]
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            meal_ids = request.form.getlist(f'meal_{meal_type}[]')
            for m_id in meal_ids:
                if m_id:
                    cursor.execute("""
                        INSERT INTO custom_diet_plan_meals (plan_id, meal_type, meal_id)
                        VALUES (%s, %s, %s)
                    """, (plan_id, meal_type, m_id))
                    
        conn.commit()
        flash("Diet Plan assigned to client successfully!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for('pro_diet_bp.assigned_plans'))
        
    cursor.close()
    conn.close()
    
    # Prefill client if passed in query param
    prefill_client = request.args.get('client')
    
    return render_template('professional/diet_plan_create.html', clients=clients, meals=meals, prefill_client=prefill_client)

@pro_diet_bp.route('/plans')
@pro_required
def assigned_plans():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT dp.*, u.name as client_name 
        FROM custom_diet_plans dp
        JOIN users u ON dp.user_id = u.id
        WHERE dp.professional_id = %s
        ORDER BY dp.created_at DESC
    """, (prof_id,))
    plans = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('professional/diet_plans.html', plans=plans)
