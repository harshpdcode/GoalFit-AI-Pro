from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_connection import get_db_connection

auth_bp = Blueprint('auth', __name__)


# ================= REGISTER ================= #

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Is your MySQL server running?", "danger")
            return redirect(url_for('auth.register'))
            
        cursor = conn.cursor(dictionary=True, buffered=True)

        try:
            # Check duplicate email
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            existing = cursor.fetchone()

            if existing:
                flash("Email already registered!", "danger")
                return redirect(url_for('auth.register'))

            # Insert user with hashed password (role defaults to 'user')
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, 'user')
            """, (name, email, hashed_password))

            # Log the registration
            try:
                user_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO activity_logs (user_id, action, details) VALUES (%s, %s, %s)",
                    (user_id, 'register', f'New user registered: {email}')
                )
            except:
                pass

            flash("Registration Successful!", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            print("REGISTER ERROR:", e)
            flash("Registration failed. Check console.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/register.html')


# ================= LOGIN ================= #

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Is your MySQL server running?", "danger")
            return redirect(url_for('auth.login'))
            
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("""
            SELECT * FROM users
            WHERE email=%s
        """, (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):

            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['email'] = user['email']
            session['role'] = user.get('role', 'user')

            # Log the login
            try:
                cursor.execute(
                    "INSERT INTO activity_logs (user_id, action, details) VALUES (%s, %s, %s)",
                    (user['id'], 'login', f'{user["name"]} logged in')
                )
            except:
                pass

            # Admin redirect
            if user.get('role') == 'admin':
                cursor.close()
                conn.close()
                return redirect(url_for('admin.admin_dashboard'))

            # Check health profile for regular users
            cursor.execute("""
                SELECT * FROM user_health
                WHERE user_id=%s
            """, (user['id'],))

            health = cursor.fetchone()

            cursor.close()
            conn.close()

            if not health:
                session['first_time_login'] = True
                return redirect(url_for('health.health_profile'))

            session['first_time_login'] = False
            return redirect(url_for('dashboard.dashboard'))

        else:
            flash("Invalid Email or Password", "danger")

            cursor.close()
            conn.close()

    return render_template('auth/login.html')


# ================= LOGOUT ================= #

@auth_bp.route('/logout')
def logout():
    # Log logout
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO activity_logs (user_id, action, details) VALUES (%s, %s, %s)",
                    (session['user_id'], 'logout', f'{session.get("user_name", "User")} logged out')
                )
                conn.commit()
                cursor.close()
                conn.close()
        except:
            pass
    session.clear()
    return redirect(url_for('auth.login'))