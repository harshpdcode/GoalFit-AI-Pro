from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.professional_dashboard import pro_required, get_db_connection

pro_transformations_bp = Blueprint('pro_transformations_bp', __name__, url_prefix='/pro/transformations')

@pro_transformations_bp.route('/')
@pro_required
def gallery():
    prof_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transformations WHERE professional_id = %s ORDER BY id DESC", (prof_id,))
    transformations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('professional/transformations.html', transformations=transformations)

@pro_transformations_bp.route('/add', methods=['GET', 'POST'])
@pro_required
def add_transformation():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        before_weight = request.form.get('before_weight')
        after_weight = request.form.get('after_weight')
        duration = request.form.get('duration')
        description = request.form.get('description', '')
        prof_id = session.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transformations (professional_id, client_name, before_weight, after_weight, duration, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (prof_id, client_name, before_weight, after_weight, duration, description))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Transformation added successfully!", "success")
        return redirect(url_for('pro_transformations_bp.gallery'))
    return render_template('professional/transformation_add.html')
