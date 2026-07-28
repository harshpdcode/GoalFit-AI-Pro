import os, time, json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modules.professional_dashboard import pro_required, get_db_connection
from werkzeug.utils import secure_filename

coaching_packages_bp = Blueprint('coaching_packages_bp', __name__, url_prefix='/pro/packages')

def ensure_packages_table(cursor):
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS professional_coaching_packages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            professional_id INT,
            package_name VARCHAR(150),
            short_description TEXT,
            thumbnail VARCHAR(255) DEFAULT 'static/images/packages/default_pkg.jpg',
            original_price FLOAT,
            discount_percent FLOAT DEFAULT 0,
            final_price FLOAT,
            duration_weeks VARCHAR(50),
            goals_covered TEXT,
            suitable_for TEXT,
            include_diet BOOLEAN DEFAULT TRUE,
            meals_per_day INT DEFAULT 4,
            meal_preferences TEXT,
            custom_calories BOOLEAN DEFAULT TRUE,
            workout_type VARCHAR(50) DEFAULT 'Both',
            workout_days INT DEFAULT 5,
            workout_level VARCHAR(50) DEFAULT 'Intermediate',
            weekly_schedule TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)
    except Exception as e:
        print(f"ensure_packages_table note: {e}")

@coaching_packages_bp.route('')
@coaching_packages_bp.route('/')
@pro_required
def list_packages():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    ensure_packages_table(cursor)
    
    cursor.execute("""
        SELECT * FROM professional_coaching_packages
        WHERE professional_id = %s
        ORDER BY id DESC
    """, (prof_id,))
    packages = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('professional/packages_list.html', packages=packages)

@coaching_packages_bp.route('/create', methods=['GET', 'POST'])
@pro_required
def create_package():
    if request.method == 'POST':
        prof_id = session.get('user_id')
        package_name = request.form.get('package_name')
        short_description = request.form.get('short_description')
        
        # Thumbnail upload
        thumbnail = 'static/images/packages/default_pkg.jpg'
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'uploads', 'packages')
                os.makedirs(upload_dir, exist_ok=True)
                s_filename = secure_filename(file.filename)
                filename = f"pkg_{prof_id}_{int(time.time())}_{s_filename}"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                thumbnail = file_path.replace('\\', '/')

        original_price = float(request.form.get('price', 2999))
        discount_percent = float(request.form.get('discount', 0))
        final_price = round(original_price * (1.0 - (discount_percent / 100.0)), 2)
        
        duration_weeks = request.form.get('duration_weeks', '12 Weeks')
        
        # Multi-select array fields stored as JSON strings
        goals_list = request.form.getlist('goals_covered')
        goals_covered = json.dumps(goals_list)
        
        suitable_list = request.form.getlist('suitable_for')
        suitable_for = json.dumps(suitable_list)
        
        include_diet = True if request.form.get('include_diet') == 'on' else False
        meals_per_day = int(request.form.get('meals_per_day', 4))
        meal_prefs = json.dumps(request.form.getlist('meal_preference'))
        custom_calories = True if request.form.get('custom_calories') == 'on' else False
        
        workout_type = request.form.get('workout_type', 'Both')
        workout_days = int(request.form.get('workout_days', 5))
        workout_level = request.form.get('workout_level', 'Intermediate')
        
        # Weekly Schedule
        weekly_sched = {
            'Monday': request.form.get('sched_monday', 'Chest'),
            'Tuesday': request.form.get('sched_tuesday', 'Back'),
            'Wednesday': request.form.get('sched_wednesday', 'Legs'),
            'Thursday': request.form.get('sched_thursday', 'Shoulders'),
            'Friday': request.form.get('sched_friday', 'Arms'),
            'Saturday': request.form.get('sched_saturday', 'Cardio'),
            'Sunday': request.form.get('sched_sunday', 'Rest')
        }
        weekly_schedule = json.dumps(weekly_sched)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into professional_coaching_packages
        cursor.execute("""
            INSERT INTO professional_coaching_packages
            (professional_id, package_name, short_description, thumbnail, original_price,
             discount_percent, final_price, duration_weeks, goals_covered, suitable_for,
             include_diet, meals_per_day, meal_preferences, custom_calories, workout_type,
             workout_days, workout_level, weekly_schedule)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (prof_id, package_name, short_description, thumbnail, original_price,
              discount_percent, final_price, duration_weeks, goals_covered, suitable_for,
              include_diet, meals_per_day, meal_prefs, custom_calories, workout_type,
              workout_days, workout_level, weekly_schedule))
              
        # Also sync to professional_pricing table for marketplace compatibility
        cursor.execute("""
            INSERT INTO professional_pricing (professional_id, plan_type, duration_days, price, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (prof_id, package_name, 84, final_price, short_description))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Coaching package created successfully!", "success")
        return redirect(url_for('coaching_packages_bp.list_packages'))
        
    return render_template('professional/package_create.html')

@coaching_packages_bp.route('/delete/<int:package_id>', methods=['POST'])
@pro_required
def delete_package(package_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM professional_coaching_packages WHERE id=%s AND professional_id=%s", (package_id, prof_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Coaching package deleted.", "info")
    return redirect(url_for('coaching_packages_bp.list_packages'))

@coaching_packages_bp.route('/edit/<int:package_id>', methods=['GET', 'POST'])
@pro_required
def edit_package(package_id):
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM professional_coaching_packages WHERE id=%s AND professional_id=%s", (package_id, prof_id))
    pkg = cursor.fetchone()
    
    if not pkg:
        flash("Coaching package not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('coaching_packages_bp.list_packages'))
        
    if request.method == 'POST':
        package_name = request.form.get('package_name')
        short_description = request.form.get('short_description')
        
        thumbnail = pkg['thumbnail']
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename != '':
                upload_dir = os.path.join('static', 'uploads', 'packages')
                os.makedirs(upload_dir, exist_ok=True)
                s_filename = secure_filename(file.filename)
                filename = f"pkg_{prof_id}_{int(time.time())}_{s_filename}"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                thumbnail = file_path.replace('\\', '/')

        original_price = float(request.form.get('price', pkg['original_price']))
        discount_percent = float(request.form.get('discount', pkg['discount_percent']))
        final_price = round(original_price * (1.0 - (discount_percent / 100.0)), 2)
        duration_weeks = request.form.get('duration_weeks', pkg['duration_weeks'])
        
        goals_covered = json.dumps(request.form.getlist('goals_covered'))
        suitable_for = json.dumps(request.form.getlist('suitable_for'))
        include_diet = True if request.form.get('include_diet') == 'on' else False
        meals_per_day = int(request.form.get('meals_per_day', 4))
        meal_prefs = json.dumps(request.form.getlist('meal_preference'))
        custom_calories = True if request.form.get('custom_calories') == 'on' else False
        
        workout_type = request.form.get('workout_type', 'Both')
        workout_days = int(request.form.get('workout_days', 5))
        workout_level = request.form.get('workout_level', 'Intermediate')
        
        weekly_sched = {
            'Monday': request.form.get('sched_monday', 'Chest'),
            'Tuesday': request.form.get('sched_tuesday', 'Back'),
            'Wednesday': request.form.get('sched_wednesday', 'Legs'),
            'Thursday': request.form.get('sched_thursday', 'Shoulders'),
            'Friday': request.form.get('sched_friday', 'Arms'),
            'Saturday': request.form.get('sched_saturday', 'Cardio'),
            'Sunday': request.form.get('sched_sunday', 'Rest')
        }
        weekly_schedule = json.dumps(weekly_sched)
        
        cursor.execute("""
            UPDATE professional_coaching_packages SET
                package_name=%s, short_description=%s, thumbnail=%s, original_price=%s,
                discount_percent=%s, final_price=%s, duration_weeks=%s, goals_covered=%s, suitable_for=%s,
                include_diet=%s, meals_per_day=%s, meal_preferences=%s, custom_calories=%s, workout_type=%s,
                workout_days=%s, workout_level=%s, weekly_schedule=%s
            WHERE id=%s AND professional_id=%s
        """, (package_name, short_description, thumbnail, original_price,
              discount_percent, final_price, duration_weeks, goals_covered, suitable_for,
              include_diet, meals_per_day, meal_prefs, custom_calories, workout_type,
              workout_days, workout_level, weekly_schedule, package_id, prof_id))
              
        conn.commit()
        cursor.close()
        conn.close()
        flash("Coaching package updated successfully!", "success")
        return redirect(url_for('coaching_packages_bp.list_packages'))
        
    # Deserialize JSON fields for GET
    try: pkg['goals_covered_list'] = json.loads(pkg['goals_covered']) if pkg.get('goals_covered') else []
    except: pkg['goals_covered_list'] = []
    
    try: pkg['suitable_for_list'] = json.loads(pkg['suitable_for']) if pkg.get('suitable_for') else []
    except: pkg['suitable_for_list'] = []
    
    try: pkg['meal_preferences_list'] = json.loads(pkg['meal_preferences']) if pkg.get('meal_preferences') else []
    except: pkg['meal_preferences_list'] = []
    
    try: pkg['weekly_schedule_dict'] = json.loads(pkg['weekly_schedule']) if pkg.get('weekly_schedule') else {}
    except: pkg['weekly_schedule_dict'] = {}
    
    cursor.close()
    conn.close()
    return render_template('professional/package_edit.html', pkg=pkg)
