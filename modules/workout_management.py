from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.professional_dashboard import pro_required, get_db_connection

pro_workout_bp = Blueprint('pro_workout_bp', __name__, url_prefix='/pro/workout')

@pro_workout_bp.route('/library')
@pro_required
def library():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM professional_workouts WHERE professional_id = %s ORDER BY id DESC", (prof_id,))
    workouts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('professional/workout_library.html', workouts=workouts)

@pro_workout_bp.route('/exercise/create', methods=['GET', 'POST'])
@pro_required
def create_workout():
    if request.method == 'POST':
        prof_id = session.get('user_id')
        workout_name = request.form.get('workout_name')
        target_muscle = request.form.get('target_muscle')
        sets = request.form.get('sets')
        reps = request.form.get('reps')
        rest_time = request.form.get('rest_time')
        instructions = request.form.get('instructions')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO professional_workouts (professional_id, workout_name, target_muscle, sets, reps, rest_time, instructions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (prof_id, workout_name, target_muscle, sets, reps, rest_time, instructions))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Exercise added to library successfully!", "success")
        return redirect(url_for('pro_workout_bp.library'))
        
    return render_template('professional/workout_create.html')

@pro_workout_bp.route('/plan/create', methods=['GET', 'POST'])
@pro_required
def create_plan():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT ca.user_id, u.name 
        FROM client_assignments ca
        JOIN users u ON ca.user_id = u.id
        WHERE ca.professional_id = %s AND ca.status = 'active'
    """, (prof_id,))
    clients = cursor.fetchall()
    
    cursor.execute("SELECT * FROM professional_workouts WHERE professional_id = %s", (prof_id,))
    exercises = cursor.fetchall()
    
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        plan_name = request.form.get('plan_name')
        goal = request.form.get('goal')
        notes = request.form.get('notes')
        
        cursor.execute("""
            INSERT INTO custom_workout_plans (user_id, professional_id, plan_name, goal, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_id, prof_id, plan_name, goal, notes))
        plan_id = cursor.lastrowid
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            ex_ids = request.form.getlist(f'workout_{day}[]')
            for ex_id in ex_ids:
                if ex_id:
                    cursor.execute("""
                        INSERT INTO custom_workout_plan_exercises (plan_id, workout_day, workout_id)
                        VALUES (%s, %s, %s)
                    """, (plan_id, day, ex_id))
                    
        conn.commit()
        flash("Workout Plan assigned to client successfully!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for('pro_workout_bp.assigned_plans'))
        
    cursor.close()
    conn.close()
    
    prefill_client = request.args.get('client')
    return render_template('professional/workout_plan_create.html', clients=clients, exercises=exercises, prefill_client=prefill_client)

@pro_workout_bp.route('/plans')
@pro_required
def assigned_plans():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT wp.*, u.name as client_name 
        FROM custom_workout_plans wp
        JOIN users u ON wp.user_id = u.id
        WHERE wp.professional_id = %s
        ORDER BY wp.created_at DESC
    """, (prof_id,))
    plans = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('professional/workout_plans.html', plans=plans)
