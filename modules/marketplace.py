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
        WHERE p.role IN ('trainer', 'both') AND (p.is_banned IS NULL OR p.is_banned = FALSE)
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
        WHERE p.role IN ('dietician', 'both') AND (p.is_banned IS NULL OR p.is_banned = FALSE)
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

    if not professional or professional.get('is_banned'):
        flash('This professional profile is currently unavailable.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('marketplace.trainers_list'))

    cursor.execute("SELECT * FROM professional_pricing WHERE professional_id=%s", (prof_id,))
    pricing_plans = cursor.fetchall()

    cursor.execute("SELECT * FROM transformations WHERE professional_id=%s", (prof_id,))
    transformations = cursor.fetchall()

    cursor.execute("""
        SELECT pr.*, u.name as user_name
        FROM professional_reviews pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.professional_id=%s
        ORDER BY pr.id DESC
    """, (prof_id,))
    reviews = cursor.fetchall()

    cursor.execute("""
        SELECT pcp.* FROM professional_coaching_packages pcp
        WHERE pcp.professional_id=%s
        ORDER BY pcp.id DESC
    """, (prof_id,))
    coaching_packages = cursor.fetchall()

    active_hire = None
    can_review = False
    if 'user_id' in session and session.get('role') == 'user':
        cursor.execute("""
            SELECT * FROM client_assignments
            WHERE user_id=%s AND professional_id=%s AND status='active'
        """, (session['user_id'], prof_id))
        active_hire = cursor.fetchone()

        cursor.execute("""
            SELECT id FROM client_assignments
            WHERE user_id=%s AND professional_id=%s
        """, (session['user_id'], prof_id))
        if cursor.fetchone():
            can_review = True

    cursor.close()
    conn.close()

    return render_template(
        'marketplace/profile.html',
        professional=professional,
        pricing_plans=pricing_plans,
        coaching_packages=coaching_packages,
        transformations=transformations,
        active_hire=active_hire,
        reviews=reviews,
        can_review=can_review
    )


@marketplace_bp.route('/rate-professional', methods=['POST'])
def rate_professional():
    if 'user_id' not in session or session.get('role') != 'user':
        flash('Please login to submit a review.', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    prof_id = request.form.get('professional_id')
    rating = float(request.form.get('rating', 5.0))
    review_text = request.form.get('review_text', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO professional_reviews (professional_id, user_id, rating, review_text)
        VALUES (%s, %s, %s, %s)
    """, (prof_id, user_id, rating, review_text))

    cursor.execute("SELECT AVG(rating) as avg_rating FROM professional_reviews WHERE professional_id=%s", (prof_id,))
    res = cursor.fetchone()
    if res and res['avg_rating']:
        new_rating = round(float(res['avg_rating']), 1)
        cursor.execute("UPDATE professionals SET rating=%s WHERE id=%s", (new_rating, prof_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Thank you for rating your coach!', 'success')
    return redirect(url_for('marketplace.profile', prof_id=prof_id))


@marketplace_bp.route('/my-professionals')
def my_professionals():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT ca.*, p.full_name as prof_name, p.role as prof_role, p.profile_photo as prof_photo,
               p.specialization, p.experience_years
        FROM client_assignments ca
        JOIN professionals p ON ca.professional_id = p.id
        WHERE ca.user_id=%s AND ca.status='active'
        ORDER BY ca.start_date DESC
    """, (session['user_id'],))
    active_professionals = cursor.fetchall()
    
    cursor.execute("""
        SELECT ca.*, p.full_name as prof_name, p.role as prof_role, p.profile_photo as prof_photo,
               p.specialization, p.experience_years
        FROM client_assignments ca
        JOIN professionals p ON ca.professional_id = p.id
        WHERE ca.user_id=%s AND ca.status='completed'
        ORDER BY ca.end_date DESC
    """, (session['user_id'],))
    past_professionals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'marketplace/my_professionals.html',
        active_professionals=active_professionals,
        past_professionals=past_professionals
    )
