from flask import Blueprint, session, request, jsonify
from database.db_connection import get_db_connection

diet_tracking_bp = Blueprint('diet_tracking', __name__, url_prefix='/api/diet')

@diet_tracking_bp.route('/toggle', methods=['POST'])
def toggle_meal():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    meal_id = data.get('meal_id')
    is_completed = data.get('is_completed')
    log_date = data.get('log_date')
    
    if meal_id is None or is_completed is None or not log_date:
        return jsonify({'error': 'Missing parameters'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if a log exists for this date and meal
    cursor.execute("""
        SELECT id FROM diet_logs 
        WHERE user_id = %s AND meal_id = %s AND log_date = %s
    """, (session['user_id'], meal_id, log_date))
    log = cursor.fetchone()
    
    if log:
        cursor.execute("""
            UPDATE diet_logs SET is_completed = %s 
            WHERE id = %s
        """, (is_completed, log[0]))
    else:
        cursor.execute("""
            INSERT INTO diet_logs (user_id, meal_id, log_date, is_completed)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], meal_id, log_date, is_completed))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'is_completed': is_completed})
