from flask import Blueprint, session, request, jsonify
from database.db_connection import get_db_connection

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_user_id = session['user_id']
    current_role = session.get('role', 'user')
    other_id = request.args.get('other_id')
    other_role = request.args.get('other_role')
    
    if not other_id or not other_role:
        return jsonify({'error': 'Missing parameters'}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM chat_messages 
        WHERE (sender_id = %s AND sender_role = %s AND receiver_id = %s AND receiver_role = %s)
           OR (sender_id = %s AND sender_role = %s AND receiver_id = %s AND receiver_role = %s)
        ORDER BY timestamp ASC
    """, (current_user_id, current_role, other_id, other_role,
          other_id, other_role, current_user_id, current_role))
          
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(messages)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    current_user_id = session['user_id']
    current_role = session.get('role', 'user')
    
    data = request.json
    receiver_id = data.get('receiver_id')
    receiver_role = data.get('receiver_role')
    message = data.get('message')
    
    if not receiver_id or not receiver_role or not message:
        return jsonify({'error': 'Missing parameters'}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
        
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_messages (sender_id, sender_role, receiver_id, receiver_role, message)
        VALUES (%s, %s, %s, %s, %s)
    """, (current_user_id, current_role, receiver_id, receiver_role, message))
    
    conn.commit()
    msg_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message_id': msg_id})
