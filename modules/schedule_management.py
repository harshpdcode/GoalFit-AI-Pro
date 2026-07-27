from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modules.professional_dashboard import pro_required, get_db_connection
from datetime import datetime

pro_schedule_bp = Blueprint('pro_schedule_bp', __name__, url_prefix='/pro/schedule')
user_schedule_bp = Blueprint('user_schedule_bp', __name__, url_prefix='/user/schedule')

@pro_schedule_bp.route('/')
@pro_required
def appointments():
    prof_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.*, u.name as user_name, u.email as user_email
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.professional_id = %s
        ORDER BY a.appointment_date DESC, a.appointment_time ASC
    """, (prof_id,))
    app_list = cursor.fetchall()
    
    # Format time / date for display
    for app in app_list:
        if app['appointment_date']:
            app['formatted_date'] = app['appointment_date'].strftime('%b %d, %Y')
        else:
            app['formatted_date'] = 'N/A'
            
        if app['appointment_time']:
            t = app['appointment_time']
            if hasattr(t, 'strftime'):
                app['formatted_time'] = t.strftime('%I:%M %p')
            else:
                app['formatted_time'] = str(t)
        else:
            app['formatted_time'] = 'TBD'
            
    cursor.close()
    conn.close()
    return render_template('professional/schedule.html', appointments=app_list)

@pro_schedule_bp.route('/appointment/<int:app_id>/status', methods=['POST'])
@pro_required
def update_status(app_id):
    new_status = request.form.get('status')
    if not new_status:
        flash("Status is required", "danger")
        return redirect('/pro/schedule')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments SET status = %s
        WHERE id = %s AND professional_id = %s
    """, (new_status, app_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f"Appointment status updated to {new_status.title()}!", "success")
    return redirect('/pro/schedule')

@pro_schedule_bp.route('/availability', methods=['GET', 'POST'])
@pro_required
def availability():
    if request.method == 'POST':
        flash("Availability updated successfully!", "success")
        return redirect(url_for('pro_schedule_bp.appointments'))
    return render_template('professional/availability.html')

@user_schedule_bp.route('/book', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        flash("Please log in to book an appointment.", "danger")
        return redirect('/login')
        
    prof_id = request.form.get('professional_id')
    app_date = request.form.get('appointment_date')
    app_time = request.form.get('appointment_time')
    mode = request.form.get('mode', 'Online Video')
    notes = request.form.get('notes', '')
    
    if not prof_id or not app_date or not app_time:
        flash("Please fill in date, time, and coach to book.", "warning")
        return redirect('/marketplace/my-professionals')
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (professional_id, user_id, appointment_date, appointment_time, mode, status, notes)
            VALUES (%s, %s, %s, %s, %s, 'scheduled', %s)
        """, (prof_id, session['user_id'], app_date, app_time, mode, notes))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Appointment successfully scheduled with your coach!", "success")
    except Exception as e:
        flash(f"Error booking appointment: {str(e)}", "danger")
        
    return redirect('/marketplace/my-professionals')
