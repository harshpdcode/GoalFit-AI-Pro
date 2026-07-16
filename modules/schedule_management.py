from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modules.professional_dashboard import pro_required, get_db_connection

pro_schedule_bp = Blueprint('pro_schedule_bp', __name__, url_prefix='/pro/schedule')

@pro_schedule_bp.route('/')
@pro_required
def appointments():
    return render_template('professional/schedule.html')

@pro_schedule_bp.route('/availability', methods=['GET', 'POST'])
@pro_required
def availability():
    if request.method == 'POST':
        flash("Availability updated successfully!", "success")
        return redirect(url_for('pro_schedule_bp.appointments'))
    return render_template('professional/availability.html')
