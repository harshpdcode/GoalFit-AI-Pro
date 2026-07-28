from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_connection import get_db_connection

user_reminders_bp = Blueprint('user_reminders_bp', __name__, url_prefix='/user/reminders')

@user_reminders_bp.route('/', methods=['GET'])
def get_reminders():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_reminders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            breakfast_time TIME DEFAULT '08:00:00',
            lunch_time TIME DEFAULT '13:00:00',
            snack_time TIME DEFAULT '17:00:00',
            dinner_time TIME DEFAULT '20:00:00',
            workout_time TIME DEFAULT '18:00:00',
            water_interval_hours INT DEFAULT 2,
            enable_push BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    
    cursor.execute("SELECT * FROM user_reminders WHERE user_id = %s", (user_id,))
    reminders = cursor.fetchone()
    
    if not reminders:
        cursor.execute("INSERT INTO user_reminders (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        cursor.execute("SELECT * FROM user_reminders WHERE user_id = %s", (user_id,))
        reminders = cursor.fetchone()
        
    cursor.close()
    conn.close()
    
    # Convert time/timedelta to string format (HH:MM)
    for key in ['breakfast_time', 'lunch_time', 'snack_time', 'dinner_time', 'workout_time']:
        val = reminders.get(key)
        if val:
            if hasattr(val, 'strftime'):
                reminders[key] = val.strftime('%H:%M')
            else:
                reminders[key] = str(val)[:5]
        else:
            reminders[key] = '08:00'
            
    return jsonify(reminders)

@user_reminders_bp.route('/update', methods=['POST'])
def update_reminders():
    if 'user_id' not in session:
        flash("Please log in to update reminder settings.", "danger")
        return redirect('/login')
        
    user_id = session['user_id']
    b_time = request.form.get('breakfast_time', '08:00')
    l_time = request.form.get('lunch_time', '13:00')
    s_time = request.form.get('snack_time', '17:00')
    d_time = request.form.get('dinner_time', '20:00')
    w_time = request.form.get('workout_time', '18:00')
    water_interval = request.form.get('water_interval_hours', 2, type=int)
    enable_push = 1 if request.form.get('enable_push') == 'on' else 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_reminders (user_id, breakfast_time, lunch_time, snack_time, dinner_time, workout_time, water_interval_hours, enable_push)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            breakfast_time = VALUES(breakfast_time),
            lunch_time = VALUES(lunch_time),
            snack_time = VALUES(snack_time),
            dinner_time = VALUES(dinner_time),
            workout_time = VALUES(workout_time),
            water_interval_hours = VALUES(water_interval_hours),
            enable_push = VALUES(enable_push)
    """, (user_id, b_time, l_time, s_time, d_time, w_time, water_interval, enable_push))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Daily meal, workout, and water reminder times updated!", "success")
    return redirect(request.referrer or '/dashboard')

@user_reminders_bp.route('/list')
def user_notifications():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect('/login')
        
    user_id = session['user_id']
    notifs = []
    try:
        from setup_db import ensure_notifications_table
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            ensure_notifications_table(cursor)
            cursor.execute("""
                SELECT * FROM notifications 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (user_id,))
            notifs = cursor.fetchall() or []
            
            cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print("User notifications error:", e)
        
    return render_template('user/notifications.html', notifications=notifs)

