from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_connection import get_db_connection

professional_auth_bp = Blueprint('professional_auth', __name__, url_prefix='/professional')

@professional_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role')
        bio = request.form.get('bio')
        experience_years = request.form.get('experience_years')
        specialization = request.form.get('specialization')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check duplicate
        cursor.execute("SELECT id FROM professionals WHERE email=%s", (email,))
        if cursor.fetchone():
            flash("Email already registered!", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('professional_auth.register'))

        hashed_password = generate_password_hash(password)
        try:
            cursor.execute("""
                INSERT INTO professionals 
                (full_name, email, password, phone, role, bio, experience_years, specialization)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (full_name, email, hashed_password, phone, role, bio, experience_years, specialization))
            conn.commit()
            flash("Registration Successful! Please login.", "success")
            return redirect(url_for('professional_auth.login'))
        except Exception as e:
            conn.rollback()
            flash(f"Registration failed: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('professional/auth.html', action='register')

@professional_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM professionals WHERE email=%s", (email,))
        professional = cursor.fetchone()

        cursor.close()
        conn.close()

        if professional and check_password_hash(professional['password'], password):
            session['user_id'] = professional['id']
            session['user_name'] = professional['full_name']
            session['email'] = professional['email']
            session['role'] = f"prof_{professional['role']}" # e.g., prof_trainer
            
            # Redirect to appropriate dashboard
            if professional['role'] == 'trainer':
                return redirect(url_for('trainer_dashboard.dashboard'))
            elif professional['role'] == 'dietician':
                return redirect(url_for('dietician_dashboard.dashboard'))
            else: # both
                return redirect(url_for('trainer_dashboard.dashboard')) # They'll have a hybrid view later
        else:
            flash("Invalid Email or Password", "danger")

    return render_template('professional/auth.html', action='login')
