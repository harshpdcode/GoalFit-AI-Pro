from flask import Blueprint, session, redirect, url_for, flash, make_response
from database.db_connection import get_db_connection
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_generator_bp = Blueprint('pdf_generator', __name__, url_prefix='/pdf')

@pdf_generator_bp.route('/download-custom-plan')
def download_custom_plan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if user has active assignment
    cursor.execute("""
        SELECT ca.*, p.full_name as prof_name 
        FROM client_assignments ca
        JOIN professionals p ON ca.professional_id = p.id
        WHERE ca.user_id=%s AND ca.status='active'
    """, (user_id,))
    assignment = cursor.fetchone()
    
    if not assignment:
        flash("You don't have an active professional assigned to download custom plans.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard.dashboard'))
        
    # Generate PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        textColor=colors.HexColor("#007BFF"),
        alignment=1,
        spaceAfter=20
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"GoalFit AI Premium Plan", title_style))
    elements.append(Paragraph(f"<b>Prepared for:</b> {session.get('user_name')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Prepared by:</b> {assignment['prof_name']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Plan Type:</b> {assignment['plan_type']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Fetch Custom Workouts if assigned
    cursor.execute("""
        SELECT p.* FROM custom_workout_plans p
        WHERE p.user_id=%s AND p.professional_id=%s
        ORDER BY p.created_at DESC LIMIT 1
    """, (user_id, assignment['professional_id']))
    workout_plan = cursor.fetchone()
    
    if workout_plan:
        elements.append(Paragraph("Your Custom Workout Plan", styles['Heading2']))
        cursor.execute("""
            SELECT e.workout_day, w.workout_name, w.sets, w.reps 
            FROM custom_workout_plan_exercises e
            JOIN professional_workouts w ON e.workout_id = w.id
            WHERE e.plan_id=%s
            ORDER BY e.workout_day
        """, (workout_plan['id'],))
        exercises = cursor.fetchall()
        
        if exercises:
            data = [["Day", "Exercise", "Sets", "Reps"]]
            for ex in exercises:
                data.append([ex['workout_day'], ex['workout_name'], str(ex['sets']), str(ex['reps'])])
                
            t = Table(data, colWidths=[100, 200, 80, 80])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#007BFF")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F2F2F2")),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

    cursor.close()
    conn.close()
    
    doc.build(elements)
    
    pdf_value = buffer.getvalue()
    buffer.close()
    
    response = make_response(pdf_value)
    response.headers['Content-Disposition'] = f"attachment; filename=GoalFit_Custom_Plan_{user_id}.pdf"
    response.headers['Content-Type'] = 'application/pdf'
    
    return response
