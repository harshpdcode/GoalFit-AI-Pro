import os
import razorpay
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from database.db_connection import get_db_connection

payment_gateway_bp = Blueprint('payment_gateway', __name__, url_prefix='/payment')

# Try to initialize Razorpay client (fails gracefully if keys missing)
try:
    razorpay_client = razorpay.Client(
        auth=(os.getenv('RAZORPAY_KEY_ID', ''), os.getenv('RAZORPAY_KEY_SECRET', ''))
    )
except:
    razorpay_client = None

@payment_gateway_bp.route('/checkout/<int:prof_id>/<int:plan_id>', methods=['GET', 'POST'])
def checkout(prof_id, plan_id):
    if 'user_id' not in session or session.get('role') != 'user':
        flash('Please login to hire a professional.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get Professional and Plan Details
    cursor.execute("SELECT * FROM professionals WHERE id=%s", (prof_id,))
    professional = cursor.fetchone()

    cursor.execute("SELECT * FROM professional_pricing WHERE id=%s AND professional_id=%s", (plan_id, prof_id))
    plan = cursor.fetchone()

    if not professional or not plan:
        flash('Invalid plan or professional.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('marketplace.trainers_list'))

    if request.method == 'POST':
        # Create Hire Request as pending
        cursor.execute("""
            INSERT INTO hire_requests (user_id, professional_id, plan_type, goal_type, payment_status, status)
            VALUES (%s, %s, %s, %s, 'pending', 'pending')
        """, (user_id, prof_id, plan['plan_type'], 'Custom Goal'))
        hire_request_id = cursor.lastrowid
        conn.commit()

        amount_in_paise = int(plan['price'] * 100)

        # Optional: Razorpay order creation (if keys configured)
        order_id = None
        if razorpay_client and os.getenv('RAZORPAY_KEY_ID'):
            try:
                order_data = {
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'receipt': f'receipt_{hire_request_id}',
                    'payment_capture': 1
                }
                order = razorpay_client.order.create(data=order_data)
                order_id = order['id']
            except Exception as e:
                print(f"Razorpay Error: {e}")
                
        cursor.close()
        conn.close()
        
        return render_template('payment/checkout.html', 
                              professional=professional, 
                              plan=plan, 
                              hire_request_id=hire_request_id,
                              order_id=order_id,
                              key_id=os.getenv('RAZORPAY_KEY_ID', ''),
                              amount=amount_in_paise)

    cursor.close()
    conn.close()
    # Provide the pre-checkout screen
    return render_template('payment/checkout_confirm.html', professional=professional, plan=plan)

@payment_gateway_bp.route('/success', methods=['POST'])
def payment_success():
    # Typically Razorpay sends razorpay_payment_id, razorpay_order_id, razorpay_signature
    payment_id = request.form.get('razorpay_payment_id', 'mock_payment_id')
    hire_request_id = request.form.get('hire_request_id')
    amount_paid = float(request.form.get('amount', 0)) / 100.0

    # Commission Logic
    commission_pct = 0.15 # 15% Platform Commission
    commission_amount = amount_paid * commission_pct
    professional_amount = amount_paid - commission_amount

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update hire request
    cursor.execute("UPDATE hire_requests SET payment_status='paid' WHERE id=%s", (hire_request_id,))
    
    # Insert Payment record
    cursor.execute("""
        INSERT INTO payments (user_id, professional_id, hire_request_id, razorpay_payment_id, amount, commission_amount, professional_amount, payment_status)
        SELECT user_id, professional_id, id, %s, %s, %s, %s, 'paid'
        FROM hire_requests WHERE id=%s
    """, (payment_id, amount_paid, commission_amount, professional_amount, hire_request_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Payment successful! Your request has been sent to the professional.', 'success')
    return redirect(url_for('dashboard.dashboard'))
