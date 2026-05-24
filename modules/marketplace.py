from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database.db_connection import get_db_connection

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')


@marketplace_bp.route('/trainers')
def trainers_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*,
               COALESCE(MIN(pp.price), 0) AS min_price,
               COUNT(DISTINCT ca.user_id) AS client_count
        FROM professionals p
        LEFT JOIN professional_pricing pp ON pp.professional_id = p.id
        LEFT JOIN client_assignments ca ON ca.professional_id = p.id AND ca.status = 'active'
        WHERE p.role IN ('trainer', 'both')
        GROUP BY p.id
        ORDER BY p.rating DESC
    """)
    trainers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        'marketplace/list.html',
        professionals=trainers,
        title='Trainers',
        page_type='trainers',
        filter_categories=['Weight Loss', 'Muscle Building', 'HIIT', 'Yoga', 'Body Recomposition']
    )


@marketplace_bp.route('/dieticians')
def dieticians_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*,
               COALESCE(MIN(pp.price), 0) AS min_price,
               COUNT(DISTINCT ca.user_id) AS client_count
        FROM professionals p
        LEFT JOIN professional_pricing pp ON pp.professional_id = p.id
        LEFT JOIN client_assignments ca ON ca.professional_id = p.id AND ca.status = 'active'
        WHERE p.role IN ('dietician', 'both')
        GROUP BY p.id
        ORDER BY p.rating DESC
    """)
    dieticians = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        'marketplace/list.html',
        professionals=dieticians,
        title='Dieticians',
        page_type='dieticians',
        filter_categories=['Weight Loss', 'Vegan Diets', 'PCOS', 'Sports Nutrition', 'Body Recomposition']
    )


@marketplace_bp.route('/profile/<int:prof_id>')
def profile(prof_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM professionals WHERE id=%s", (prof_id,))
    professional = cursor.fetchone()

    if not professional:
        flash('Professional not found.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.dashboard'))

    cursor.execute("SELECT * FROM professional_pricing WHERE professional_id=%s", (prof_id,))
    pricing_plans = cursor.fetchall()

    cursor.execute("SELECT * FROM transformations WHERE professional_id=%s", (prof_id,))
    transformations = cursor.fetchall()

    active_hire = None
    if 'user_id' in session and session.get('role') == 'user':
        cursor.execute("""
            SELECT * FROM client_assignments
            WHERE user_id=%s AND professional_id=%s AND status='active'
        """, (session['user_id'], prof_id))
        active_hire = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'marketplace/profile.html',
        professional=professional,
        pricing_plans=pricing_plans,
        transformations=transformations,
        active_hire=active_hire
    )
