from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from database.db_connection import get_db_connection

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not subject or not message:
            flash("Please fill in both subject and message.", "danger")
            return redirect(url_for('feedback.feedback_form'))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user_feedback (user_id, subject, message)
            VALUES (%s, %s, %s)
        """, (user_id, subject, message))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Thank you! Your feedback has been submitted successfully.", "success")
        return redirect(url_for('feedback.feedback_form'))

    # Fetch user's past feedback
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT * FROM user_feedback 
        WHERE user_id=%s 
        ORDER BY created_at DESC
    """, (user_id,))
    my_feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('user/feedback_form.html',
        feedbacks=my_feedbacks,
        user_name=session.get('user_name'),
        email=session.get('email')
    )
