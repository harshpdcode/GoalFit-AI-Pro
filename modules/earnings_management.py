from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.professional_dashboard import pro_required, get_db_connection

pro_earnings_bp = Blueprint('pro_earnings_bp', __name__, url_prefix='/pro/earnings')

@pro_earnings_bp.route('/')
@pro_required
def earnings():
    return render_template('professional/earnings.html')

@pro_earnings_bp.route('/transactions')
@pro_required
def transactions():
    return render_template('professional/transactions.html')

@pro_earnings_bp.route('/commission')
@pro_required
def commission():
    return render_template('professional/commission.html')
