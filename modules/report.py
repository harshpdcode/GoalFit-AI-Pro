from flask import Blueprint, session, redirect, url_for, make_response
from database.db_connection import get_db_connection
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import date

report_bp = Blueprint('report', __name__)


@report_bp.route('/download-report')
def download_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user_name = session.get('user_name', 'User')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Fetch all data
    cursor.execute("SELECT * FROM user_health WHERE user_id=%s", (user_id,))
    health = cursor.fetchone()

    cursor.execute("SELECT * FROM bmi_records WHERE user_id=%s ORDER BY recorded_date DESC LIMIT 5", (user_id,))
    bmi_records = cursor.fetchall()

    cursor.execute("SELECT * FROM progress_logs WHERE user_id=%s ORDER BY log_date DESC LIMIT 10", (user_id,))
    progress = cursor.fetchall()

    cursor.execute("SELECT * FROM goal_predictions WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
    prediction = cursor.fetchone()

    cursor.execute("SELECT * FROM step_recommendations WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
    steps = cursor.fetchone()

    # Fetch diet plan
    diet_meals = []
    if health:
        cursor.execute("""
            SELECT meal_name, meal_time, calories, proteins, carbs, fats 
            FROM diet_meals 
            WHERE goal_type=%s AND diet_type=%s 
            ORDER BY meal_time, option_group
        """, (health.get('goal_type', ''), health.get('diet_preference', '')))
        diet_meals = cursor.fetchall()

    cursor.close()
    conn.close()

    # ======= BUILD PDF =======
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()

    # Custom Styles
    accent = HexColor('#12d6c5')
    dark = HexColor('#0f172a')
    gray = HexColor('#6b7280')
    white = HexColor('#ffffff')

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
        fontSize=28, textColor=accent, spaceAfter=6, alignment=TA_CENTER,
        fontName='Helvetica-Bold')

    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
        fontSize=11, textColor=gray, alignment=TA_CENTER, spaceAfter=20)

    section_style = ParagraphStyle('SectionHead', parent=styles['Heading2'],
        fontSize=16, textColor=accent, spaceBefore=20, spaceAfter=10,
        fontName='Helvetica-Bold', borderWidth=0)

    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#374151'), spaceAfter=4)

    elements = []

    # ===== HEADER =====
    elements.append(Paragraph("⚡ GOALFIT AI", title_style))
    elements.append(Paragraph("Health & Fitness Report", subtitle_style))
    elements.append(Paragraph(f"Generated for: <b>{user_name}</b> | Date: {date.today().strftime('%B %d, %Y')}", 
        ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=gray, alignment=TA_CENTER, spaceAfter=5)))
    elements.append(HRFlowable(width="100%", thickness=2, color=accent, spaceAfter=15))

    # ===== HEALTH PROFILE =====
    if health:
        elements.append(Paragraph("📋 Health Profile", section_style))
        
        profile_data = [
            ['Parameter', 'Value'],
            ['Age', f"{health.get('age', '—')} years"],
            ['Gender', health.get('gender', '—')],
            ['Height', f"{health.get('height_cm', '—')} cm"],
            ['Current Weight', f"{health.get('weight_kg', '—')} kg"],
            ['Target Weight', f"{health.get('target_weight', '—')} kg"],
            ['Activity Level', health.get('activity_level', '—')],
            ['Goal Type', health.get('goal_type', '—')],
            ['Diet Preference', health.get('diet_preference', '—')],
        ]

        t = Table(profile_data, colWidths=[200, 280])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), accent),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8fafc'), HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # ===== BMI HISTORY =====
    if bmi_records:
        elements.append(Paragraph("📊 BMI History (Last 5 Records)", section_style))
        
        bmi_data = [['Date', 'BMI Value', 'Category']]
        for r in bmi_records:
            bmi_data.append([
                str(r.get('recorded_date', '—')),
                str(r.get('bmi_value', '—')),
                r.get('bmi_category', '—')
            ])

        t = Table(bmi_data, colWidths=[160, 160, 160])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), accent),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8fafc'), HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # ===== GOAL PREDICTION =====
    if prediction:
        elements.append(Paragraph("🎯 AI Goal Prediction", section_style))
        
        pred_data = [
            ['Metric', 'Value'],
            ['Current Weight', f"{prediction.get('current_weight', '—')} kg"],
            ['Target Weight', f"{prediction.get('target_weight', '—')} kg"],
            ['Weekly Change Rate', f"{prediction.get('weekly_change_rate', '—')} kg/week"],
            ['Estimated Weeks', str(prediction.get('estimated_weeks', '—'))],
            ['Estimated Completion', str(prediction.get('estimated_completion_date', '—'))],
        ]

        t = Table(pred_data, colWidths=[240, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#faf5ff'), HexColor('#f5f3ff')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # ===== STEP RECOMMENDATIONS =====
    if steps:
        elements.append(Paragraph("👣 Daily Step Recommendation", section_style))
        elements.append(Paragraph(f"• Daily Steps Target: <b>{steps.get('daily_steps', '—')}</b>", normal_style))
        elements.append(Paragraph(f"• Calories to Burn: <b>{steps.get('calories_to_burn', '—')} kcal</b>", normal_style))
        elements.append(Paragraph(f"• Walking Distance: <b>{steps.get('distance_km', '—')} km</b>", normal_style))
        elements.append(Spacer(1, 10))

    # ===== WEIGHT PROGRESS =====
    if progress:
        elements.append(Paragraph("📈 Weight Progress Log (Last 10)", section_style))
        
        prog_data = [['Date', 'Weight (kg)']]
        for p in progress:
            prog_data.append([str(p.get('log_date', '—')), str(p.get('weight_kg', '—'))])

        t = Table(prog_data, colWidths=[240, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0ea5e9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f0f9ff'), HexColor('#e0f2fe')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # ===== DIET PLAN =====
    if diet_meals:
        elements.append(Paragraph("🍽️ Your Diet Plan", section_style))
        
        diet_data = [['Meal', 'Time', 'Calories', 'Protein', 'Carbs', 'Fats']]
        for m in diet_meals:
            diet_data.append([
                m.get('meal_name', ''),
                m.get('meal_time', ''),
                f"{m.get('calories', '')} kcal",
                f"{m.get('proteins', '')}g",
                f"{m.get('carbs', '')}g",
                f"{m.get('fats', '')}g",
            ])

        t = Table(diet_data, colWidths=[120, 70, 70, 60, 60, 60])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f0fdf4'), HexColor('#ecfdf5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)

    # ===== FOOTER =====
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0'), spaceAfter=10))
    elements.append(Paragraph(
        "This report was auto-generated by GoalFit AI. For personalized advice, consult a healthcare professional.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=gray, alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=GoalFit_Report_{user_name}_{date.today()}.pdf'

    return response
