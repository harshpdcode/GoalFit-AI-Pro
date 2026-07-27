import os
from flask import Blueprint, session, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from database.db_connection import get_db_connection
from datetime import datetime

progress_gallery_bp = Blueprint('progress_gallery', __name__, url_prefix='/gallery')

UPLOAD_FOLDER = 'static/images/progress_photos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@progress_gallery_bp.route('/')
def gallery():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM progress_photos 
        WHERE user_id = %s 
        ORDER BY log_date DESC, id DESC
    """, (session['user_id'],))
    photos = cursor.fetchall()
    
    # Check if user has an active professional
    cursor.execute("""
        SELECT p.id as professional_id, p.full_name as prof_name, p.role as prof_role, p.profile_photo as prof_photo 
        FROM client_assignments ca
        JOIN professionals p ON ca.professional_id = p.id
        WHERE ca.user_id = %s AND ca.status = 'active' LIMIT 1
    """, (session['user_id'],))
    pro = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('progress_gallery.html', photos=photos, hired_pro=pro)

@progress_gallery_bp.route('/upload', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if 'photo' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(f"user_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        db_path = f"{UPLOAD_FOLDER}/{filename}"
        log_date = datetime.now().date()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO progress_photos (user_id, photo_path, log_date, is_shared)
            VALUES (%s, %s, %s, FALSE)
        """, (session['user_id'], db_path, log_date))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('progress_gallery.gallery'))

@progress_gallery_bp.route('/toggle_share', methods=['POST'])
def toggle_share():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    photo_id = data.get('photo_id')
    is_shared = data.get('is_shared')
    
    if photo_id is None or is_shared is None:
        return jsonify({'error': 'Missing parameters'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE progress_photos SET is_shared = %s 
        WHERE id = %s AND user_id = %s
    """, (is_shared, photo_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'is_shared': is_shared})

@progress_gallery_bp.route('/client/<int:client_id>')
def client_gallery(client_id):
    allowed_pro_roles = ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_dietician', 'prof_both']
    if 'user_id' not in session or session.get('role') not in allowed_pro_roles:
        return redirect('/pro/login')
        
    prof_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify assignment
    cursor.execute("SELECT * FROM client_assignments WHERE professional_id=%s AND user_id=%s AND status='active'", (prof_id, client_id))
    assignment = cursor.fetchone()
    if not assignment:
        flash("You do not have access to this client's gallery.", "danger")
        cursor.close()
        conn.close()
        return redirect('/pro/clients')
        
    cursor.execute("SELECT * FROM users WHERE id=%s", (client_id,))
    client_user = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as total FROM progress_photos WHERE user_id = %s", (client_id,))
    res_count = cursor.fetchone()
    total_photos = res_count['total'] if res_count else 0
    
    cursor.execute("""
        SELECT * FROM progress_photos 
        WHERE user_id = %s AND is_shared = TRUE
        ORDER BY log_date DESC, id DESC
    """, (client_id,))
    photos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('professional/client_gallery.html', photos=photos, client=client_user, total_photos=total_photos)

@progress_gallery_bp.route('/client/<int:client_id>/request_access', methods=['POST'])
def request_photo_access(client_id):
    allowed_pro_roles = ['trainer', 'dietician', 'both', 'prof_trainer', 'prof_dietician', 'prof_both']
    if 'user_id' not in session or session.get('role') not in allowed_pro_roles:
        return redirect('/pro/login')
        
    prof_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT full_name FROM professionals WHERE id=%s", (prof_id,))
    prof = cursor.fetchone()
    prof_name = prof['full_name'] if prof else 'Your Coach'
    
    msg = f"📸 {prof_name} has requested access to view your progress photos. Please toggle photo sharing in your Progress Gallery!"
    
    cursor.execute("""
        INSERT INTO chat_messages (sender_id, sender_role, receiver_id, receiver_role, message)
        VALUES (%s, 'trainer', %s, 'user', %s)
    """, (prof_id, client_id, msg))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Photo access request sent to client via chat!", "success")
    return redirect(f"/gallery/client/{client_id}")
