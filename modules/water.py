from flask import Blueprint, session, redirect, url_for, render_template, request, jsonify
from database.db_connection import get_db_connection
from datetime import date

water_bp = Blueprint('water', __name__)


@water_bp.route('/water-tracker')
def water_tracker():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    today = date.today()

    # Get today's log
    cursor.execute("""
        SELECT * FROM water_logs 
        WHERE user_id=%s AND log_date=%s
    """, (user_id, today))
    water_log = cursor.fetchone()

    if not water_log:
        # Create today's entry
        cursor.execute("""
            INSERT INTO water_logs (user_id, glasses, goal_glasses, log_date)
            VALUES (%s, 0, 8, %s)
        """, (user_id, today))
        conn.commit()
        water_log = {'glasses': 0, 'goal_glasses': 8, 'log_date': today}

    # Get streak (consecutive days meeting goal)
    cursor.execute("""
        SELECT log_date, glasses, goal_glasses 
        FROM water_logs 
        WHERE user_id=%s AND log_date < %s
        ORDER BY log_date DESC 
        LIMIT 30
    """, (user_id, today))
    past_logs = cursor.fetchall()

    streak = 0
    for log in past_logs:
        if log['glasses'] >= log['goal_glasses']:
            streak += 1
        else:
            break

    # Check if today's goal is met
    if water_log['glasses'] >= water_log['goal_glasses']:
        streak += 1

    # Week history (last 7 days)
    cursor.execute("""
        SELECT log_date, glasses, goal_glasses 
        FROM water_logs 
        WHERE user_id=%s 
        ORDER BY log_date DESC LIMIT 7
    """, (user_id,))
    week_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('user/water_tracker.html',
        water_log=water_log,
        streak=streak,
        week_history=week_history,
        user_name=session.get('user_name'),
        email=session.get('email')
    )


@water_bp.route('/water-tracker/add', methods=['POST'])
def add_water():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    today = date.today()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Check if log exists for today
    cursor.execute("""
        SELECT * FROM water_logs WHERE user_id=%s AND log_date=%s
    """, (user_id, today))
    log = cursor.fetchone()

    if log:
        new_glasses = log['glasses'] + 1
        cursor.execute("""
            UPDATE water_logs SET glasses=%s WHERE user_id=%s AND log_date=%s
        """, (new_glasses, user_id, today))
    else:
        new_glasses = 1
        cursor.execute("""
            INSERT INTO water_logs (user_id, glasses, goal_glasses, log_date)
            VALUES (%s, 1, 8, %s)
        """, (user_id, today))

    conn.commit()

    # Get goal
    cursor.execute("SELECT goal_glasses FROM water_logs WHERE user_id=%s AND log_date=%s", (user_id, today))
    goal = cursor.fetchone()['goal_glasses']

    cursor.close()
    conn.close()

    return jsonify({
        'glasses': new_glasses,
        'goal': goal,
        'percentage': min(100, round((new_glasses / goal) * 100))
    })


@water_bp.route('/water-tracker/remove', methods=['POST'])
def remove_water():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    today = date.today()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT * FROM water_logs WHERE user_id=%s AND log_date=%s
    """, (user_id, today))
    log = cursor.fetchone()

    if log and log['glasses'] > 0:
        new_glasses = log['glasses'] - 1
        cursor.execute("""
            UPDATE water_logs SET glasses=%s WHERE user_id=%s AND log_date=%s
        """, (new_glasses, user_id, today))
        conn.commit()
    else:
        new_glasses = 0

    goal = log['goal_glasses'] if log else 8

    cursor.close()
    conn.close()

    return jsonify({
        'glasses': new_glasses,
        'goal': goal,
        'percentage': min(100, round((new_glasses / goal) * 100))
    })


@water_bp.route('/water-tracker/set-goal', methods=['POST'])
def set_water_goal():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    today = date.today()
    new_goal = int(request.json.get('goal', 8))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE water_logs SET goal_glasses=%s WHERE user_id=%s AND log_date=%s
    """, (new_goal, user_id, today))

    if cursor.rowcount == 0:
        cursor.execute("""
            INSERT INTO water_logs (user_id, glasses, goal_glasses, log_date)
            VALUES (%s, 0, %s, %s)
        """, (user_id, new_goal, today))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'goal': new_goal})
