"""
GoalFit AI Pro - Full Testing Seed Script
Adds rich demo data: professionals, users, assignments, diet plans, workout plans, reviews, etc.
Run: python seed_data.py
"""
import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import datetime

load_dotenv()

from database.db_connection import get_db_connection

def get_conn():
    return get_db_connection()

def seed():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    # ─────────────────────────────────────────────
    # 1. ADD MISSING COLUMNS (safe ALTER TABLE)
    # ─────────────────────────────────────────────
    print("Applying schema patches...")

    def add_col_if_missing(table, column, col_def):
        cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
        if not cursor.fetchone():
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            conn.commit()
            print(f"  Added column {table}.{column}")

    add_col_if_missing("transformations",  "created_at",       "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    add_col_if_missing("custom_diet_plans","notes",            "TEXT")
    add_col_if_missing("custom_workout_plans","notes",         "TEXT")
    add_col_if_missing("professionals",    "approval_status",  "VARCHAR(30) DEFAULT 'approved'")


    # ─────────────────────────────────────────────
    # 2. CLEAR OLD DEMO DATA (keep schema)
    # ─────────────────────────────────────────────
    print("Clearing old demo data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    for tbl in [
        "notifications", "professional_reviews", "professional_settings",
        "appointments", "professional_availability",
        "custom_workout_plan_exercises", "custom_workout_plans",
        "custom_diet_plan_meals", "custom_diet_plans",
        "professional_workouts", "professional_meals",
        "transformations", "payments", "hire_requests",
        "client_assignments", "professional_pricing",
        "progress_photos", "progress_logs", "bmi_records",
        "goal_predictions", "step_recommendations", "activity_logs",
        "user_health", "users", "professionals",
    ]:
        cursor.execute(f"DELETE FROM {tbl}")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()

    pw = generate_password_hash("password123")
    admin_pw = generate_password_hash("admin123")
    today = datetime.date.today()

    # ─────────────────────────────────────────────
    # 3. USERS
    # ─────────────────────────────────────────────
    print("Seeding users...")
    users = [
        (1, "Admin",         "admin@goalfit.ai",    admin_pw, "admin"),
        (2, "Harsh Pandya",  "harsh@goalfit.ai",    pw,       "user"),
        (3, "Rahul Sharma",  "rahul@test.com",      pw,       "user"),
        (4, "Priya Verma",   "priya@test.com",      pw,       "user"),
        (5, "Arjun Singh",   "arjun@test.com",      pw,       "user"),
        (6, "Neha Gupta",    "neha@test.com",        pw,       "user"),
    ]
    cursor.executemany(
        "INSERT INTO users (id, name, email, password, role) VALUES (%s,%s,%s,%s,%s)",
        users
    )

    # Health profiles
    health = [
        (2, 23, "Male",   175, 82.0, 72.0,  "Moderate",    "Weight Loss",  "Non-Vegetarian"),
        (3, 28, "Male",   180, 95.0, 80.0,  "Active",      "Muscle Gain",  "Non-Vegetarian"),
        (4, 25, "Female", 162, 58.0, 52.0,  "Lightly Active","Weight Loss", "Vegetarian"),
        (5, 30, "Male",   170, 70.0, 78.0,  "Active",      "Muscle Gain",  "Non-Vegetarian"),
        (6, 22, "Female", 158, 55.0, 53.0,  "Moderate",    "Weight Loss",  "Vegan"),
    ]
    cursor.executemany(
        "INSERT INTO user_health (user_id,age,gender,height_cm,weight_kg,target_weight,activity_level,goal_type,diet_preference) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        health
    )

    # BMI, progress
    for uid, bmi, cat, wt in [(2,26.8,"Overweight",82),(3,29.3,"Overweight",95),(4,22.1,"Normal",58),(5,24.2,"Normal",70),(6,22.0,"Normal",55)]:
        cursor.execute("INSERT INTO bmi_records (user_id,bmi_value,bmi_category,recorded_date) VALUES (%s,%s,%s,%s)", (uid,bmi,cat,today))
        cursor.execute("INSERT INTO progress_logs (user_id,weight_kg,log_date) VALUES (%s,%s,%s)", (uid,wt,today))
        cursor.execute("INSERT INTO step_recommendations (user_id,daily_steps,calories_to_burn,distance_km) VALUES (%s,%s,%s,%s)", (uid,8000,320,6.2))

    conn.commit()

    # ─────────────────────────────────────────────
    # 4. PROFESSIONALS
    # ─────────────────────────────────────────────
    print("Seeding professionals...")
    professionals = [
        (1, "Alex Trainer",    "alex@trainer.com",      pw, "9876543210", "trainer",
         "Elite personal trainer specializing in weight loss and bodybuilding. Helped 200+ clients.", 5,
         "Weight Loss, Muscle Building", True, 4.8, "approved"),
        (2, "Sarah Dietician", "sarah@dietician.com",   pw, "9876543211", "dietician",
         "Certified clinical nutritionist with a focus on holistic health. PCOS & vegan expert.", 8,
         "Vegan Diets, PCOS, Weight Loss", True, 4.9, "approved"),
        (3, "Mike Hybrid",     "mike@trainer.com",      pw, "9876543212", "both",
         "Complete transformation coach. I handle both your lifting and your kitchen.", 10,
         "Body Recomposition, Strength", True, 5.0, "approved"),
        (4, "Emma Coach",      "emma@dietician.com",    pw, "9876543213", "trainer",
         "HIIT and mobility expert. Transform your body in 30 days!", 3,
         "HIIT, Yoga, Flexibility", True, 4.2, "approved"),
        (5, "Dr. John",        "john@health.com",       pw, "9876543214", "dietician",
         "Expert in sports nutrition and endurance performance.", 12,
         "Sports Nutrition, Endurance", True, 4.7, "approved"),
    ]
    cursor.executemany("""
        INSERT INTO professionals
        (id,full_name,email,password,phone,role,bio,experience_years,specialization,is_verified,rating,approval_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, professionals)

    # Pricing
    pricing = [
        (1, 1, "Basic Training",          30,  2000, "4 weeks personalized workout."),
        (2, 1, "Advanced Training",       90,  5500, "12 weeks intensive coaching."),
        (3, 2, "Diet Plan - Basic",        30,  1500, "Customized diet with weekly check-ins."),
        (4, 2, "Diet Plan - Premium",      90,  4000, "3 month holistic diet coaching."),
        (5, 3, "Complete Transformation",  90,  8000, "90 days full workout + diet coaching."),
        (6, 4, "HIIT Bootcamp",            30,  2500, "30 day HIIT & mobility program."),
        (7, 5, "Sports Nutrition Plan",    60,  3500, "2 month sports nutrition package."),
    ]
    cursor.executemany(
        "INSERT INTO professional_pricing (id,professional_id,plan_type,duration_days,price,description) VALUES (%s,%s,%s,%s,%s,%s)",
        pricing
    )
    conn.commit()

    # ─────────────────────────────────────────────
    # 5. HIRE REQUESTS & CLIENT ASSIGNMENTS
    # ─────────────────────────────────────────────
    print("Seeding client assignments...")
    hire_requests = [
        (1, 2, 1, "Basic Training",         "paid", "accepted"),
        (2, 3, 3, "Complete Transformation", "paid", "accepted"),
        (3, 4, 2, "Diet Plan - Basic",       "paid", "accepted"),
        (4, 5, 3, "Complete Transformation", "paid", "accepted"),
        (5, 6, 2, "Diet Plan - Premium",     "paid", "accepted"),
    ]
    cursor.executemany(
        "INSERT INTO hire_requests (id,user_id,professional_id,plan_type,payment_status,status) VALUES (%s,%s,%s,%s,%s,%s)",
        hire_requests
    )

    # client_assignments: user_id, professional_id, plan_type, start_date, end_date, status
    assignments = [
        (2, 1, "Basic Training",         "2026-06-01", "2026-07-01", "active"),
        (3, 3, "Complete Transformation","2026-05-15", "2026-08-15", "active"),
        (4, 2, "Diet Plan - Basic",       "2026-06-10", "2026-07-10", "active"),
        (5, 3, "Complete Transformation","2026-06-01", "2026-09-01", "active"),
        (6, 2, "Diet Plan - Premium",    "2026-06-15", "2026-09-15", "active"),
    ]
    cursor.executemany(
        "INSERT INTO client_assignments (user_id,professional_id,plan_type,start_date,end_date,status) VALUES (%s,%s,%s,%s,%s,%s)",
        assignments
    )

    payments = [
        (2, 1, 1, "pay_mock_001", 2000, 300,  1700, "paid"),
        (3, 3, 2, "pay_mock_002", 8000, 1200, 6800, "paid"),
        (4, 2, 3, "pay_mock_003", 1500, 225,  1275, "paid"),
        (5, 3, 4, "pay_mock_004", 8000, 1200, 6800, "paid"),
        (6, 2, 5, "pay_mock_005", 4000, 600,  3400, "paid"),
    ]
    cursor.executemany(
        "INSERT INTO payments (user_id,professional_id,hire_request_id,razorpay_payment_id,amount,commission_amount,professional_amount,payment_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        payments
    )
    conn.commit()

    # ─────────────────────────────────────────────
    # 6. PROFESSIONAL MEALS (for Alex, Sarah, Mike)
    # ─────────────────────────────────────────────
    print("Seeding professional meals...")
    pro_meals = [
        # Alex (trainer, id=1) — workout-focused meals
        (1, "High Protein Oats",        400, 30, 45, 8,  "Rolled oats, whey protein, banana, almond milk",   "Mix oats with warm almond milk. Stir in protein. Top with banana.",    "static/images/diet/oats_ai.jpg"),
        (1, "Chicken & Rice Bowl",      550, 45, 60, 10, "Chicken breast 200g, brown rice, broccoli, olive oil","Grill chicken. Cook rice. Steam broccoli. Assemble bowl.",             "static/images/diet/dal_rice_ai.png"),
        (1, "Egg White Omelette",       300, 28, 5,  12, "Egg whites x6, spinach, bell pepper, low-fat cheese","Beat whites, pour in pan, add veggies, fold.",                        "static/images/diet/sandwich_ai.png"),
        (1, "Whey Protein Shake",       250, 40, 15, 4,  "Whey 2 scoops, banana, milk 300ml",               "Blend all. Serve cold.",                                               "static/images/diet/apple_slice.jpeg"),
        # Sarah (dietician, id=2)
        (2, "Quinoa Buddha Bowl",       420, 18, 55, 14, "Quinoa, chickpeas, roasted veggies, tahini",       "Cook quinoa. Roast veggies. Top with tahini dressing.",                "static/images/diet/chickpeas.jpeg"),
        (2, "Avocado Protein Toast",    350, 12, 30, 20, "Whole wheat bread, avocado, eggs, seeds",           "Toast bread. Mash avocado. Top with eggs and seeds.",                 "static/images/diet/sandwich.jpeg"),
        (2, "Lentil Detox Soup",        280, 15, 40, 4,  "Red lentils, spinach, tomatoes, cumin, coriander", "Boil lentils with spices. Add spinach last.",                          "static/images/diet/soup_and_roti.jpeg"),
        (2, "Green Smoothie Bowl",      260, 8,  45, 6,  "Spinach, banana, mango, coconut milk, chia seeds", "Blend smoothie. Pour. Top with chia and granola.",                    "static/images/diet/apple_slice.jpeg"),
        # Mike (both, id=3)
        (3, "Power Breakfast Plate",    650, 50, 60, 20, "Eggs x3, oats, banana, peanut butter, nuts",       "Cook eggs. Make oats. Assemble power plate.",                          "static/images/diet/sandwich_ai.png"),
        (3, "Grilled Salmon & Veggies", 480, 40, 20, 18, "Salmon fillet, asparagus, sweet potato, olive oil", "Season salmon. Grill 15 min. Roast veggies.",                         "static/images/diet/grilled_paneer_salad.jpeg"),
        (3, "Mass Gainer Shake",        700, 50, 80, 15, "Oats 100g, whey 2 scoops, milk, banana, peanut butter","Blend all until smooth. Drink post-workout.",                     "static/images/diet/oats_ai.jpg"),
        (3, "Beef & Quinoa Bowl",       620, 52, 55, 16, "Lean beef 200g, quinoa, peppers, olive oil",        "Brown beef. Cook quinoa. Mix together with veggies.",                 "static/images/diet/dal_rice_ai.png"),
    ]
    cursor.executemany(
        "INSERT INTO professional_meals (professional_id,meal_name,calories,protein,carbs,fats,ingredients,instructions,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        pro_meals
    )
    conn.commit()

    # Fetch meal IDs
    cursor.execute("SELECT id, professional_id, meal_name FROM professional_meals ORDER BY id")
    meals_map = cursor.fetchall()

    # ─────────────────────────────────────────────
    # 7. PROFESSIONAL WORKOUTS (exercises)
    # ─────────────────────────────────────────────
    print("Seeding professional workouts...")
    pro_workouts = [
        # Alex (id=1)
        (1, "Barbell Squat",      "Legs",        4, 8,  90, "Keep back straight. Drive through heels."),
        (1, "Bench Press",        "Chest",       4, 8,  90, "Control descent. Full range of motion."),
        (1, "Deadlift",           "Back",        3, 6,  120,"Keep bar close. Brace core."),
        (1, "Shoulder Press",     "Shoulders",   3, 10, 60, "Don't flare elbows. Press straight up."),
        (1, "Pull Ups",           "Back/Biceps", 3, 8,  60, "Full hang to chin over bar."),
        # Mike (id=3) — both trainer & dietician
        (3, "Romanian Deadlift",  "Hamstrings",  4, 10, 90, "Hinge at hips. Slight knee bend."),
        (3, "Cable Rows",         "Back",        3, 12, 60, "Squeeze shoulder blades. Controlled return."),
        (3, "Incline Dumbbell Press","Chest",    4, 10, 60, "30° incline. Full ROM."),
        (3, "Leg Press",          "Legs",        4, 12, 60, "Don't lock knees at top."),
        (3, "Face Pulls",         "Rear Delts",  3, 15, 45, "Pull to forehead. External rotation."),
        # Emma (id=4)
        (4, "Burpees",            "Full Body",   4, 15, 30, "Jump up explosively. Land softly."),
        (4, "Mountain Climbers",  "Abs/Cardio",  3, 30, 30, "Keep hips level. Fast pace."),
        (4, "Box Jumps",          "Legs/Power",  3, 10, 60, "Soft landing. Full extension at top."),
    ]
    cursor.executemany(
        "INSERT INTO professional_workouts (professional_id,workout_name,target_muscle,sets,reps,rest_time,instructions) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        pro_workouts
    )
    conn.commit()

    cursor.execute("SELECT id, professional_id FROM professional_workouts ORDER BY id")
    workouts_map = cursor.fetchall()

    # ─────────────────────────────────────────────
    # 8. CUSTOM DIET PLANS (assigned to clients)
    # ─────────────────────────────────────────────
    print("Seeding diet plans...")
    # Sarah (id=2) assigns plans to Priya (uid=4) and Neha (uid=6)
    # Mike (id=3) assigns plan to Rahul (uid=3) and Arjun (uid=5)
    diet_plans = [
        (4, 2, "Priya's Weight Loss Diet",   "Weight Loss", "Focus on high protein, low carb. Avoid processed sugar."),
        (6, 2, "Neha's Vegan Cut Plan",       "Weight Loss", "Plant-based, calorie deficit. High fibre intake."),
        (3, 3, "Rahul's Muscle Gain Diet",    "Muscle Gain", "Caloric surplus. High protein every 3 hours."),
        (5, 3, "Arjun's Recomp Diet",         "Body Recomp", "Moderate protein. Carb cycling on training days."),
    ]
    cursor.executemany(
        "INSERT INTO custom_diet_plans (user_id,professional_id,plan_name,goal,notes) VALUES (%s,%s,%s,%s,%s)",
        diet_plans
    )
    conn.commit()

    cursor.execute("SELECT id FROM custom_diet_plans ORDER BY id")
    diet_plan_ids = [r['id'] for r in cursor.fetchall()]

    # Assign meals to plans (grab meal IDs by pro)
    cursor.execute("SELECT id, professional_id FROM professional_meals ORDER BY id")
    pm = cursor.fetchall()
    sarah_meals = [m['id'] for m in pm if m['professional_id'] == 2]
    mike_meals  = [m['id'] for m in pm if m['professional_id'] == 3]

    def assign_meals(plan_id, meal_ids, types):
        for t, mid in zip(types, meal_ids):
            cursor.execute(
                "INSERT INTO custom_diet_plan_meals (plan_id,meal_type,meal_id) VALUES (%s,%s,%s)",
                (plan_id, t, mid)
            )

    if len(diet_plan_ids) >= 4 and len(sarah_meals) >= 4 and len(mike_meals) >= 4:
        assign_meals(diet_plan_ids[0], sarah_meals[:4], ['breakfast','lunch','dinner','snacks'])
        assign_meals(diet_plan_ids[1], sarah_meals[2:], ['breakfast','lunch','dinner','snacks'][:len(sarah_meals[2:])])
        assign_meals(diet_plan_ids[2], mike_meals[:4],  ['breakfast','lunch','dinner','snacks'])
        assign_meals(diet_plan_ids[3], mike_meals[2:],  ['breakfast','lunch','dinner','snacks'][:len(mike_meals[2:])])
    conn.commit()

    # ─────────────────────────────────────────────
    # 9. CUSTOM WORKOUT PLANS
    # ─────────────────────────────────────────────
    print("Seeding workout plans...")
    # Alex (id=1) → Harsh (uid=2)
    # Mike (id=3) → Rahul (uid=3) and Arjun (uid=5)
    workout_plans = [
        (2, 1, "Harsh's 4-Week Cut Program",      "Weight Loss",  "Focus on compound lifts. 3 days on/1 off split."),
        (3, 3, "Rahul's Strength Builder",          "Muscle Gain",  "Progressive overload. Log all PRs."),
        (5, 3, "Arjun's Body Recomp Plan",          "Body Recomp",  "Heavy days Mon/Thu. Moderate Tue/Fri."),
    ]
    cursor.executemany(
        "INSERT INTO custom_workout_plans (user_id,professional_id,plan_name,goal,notes) VALUES (%s,%s,%s,%s,%s)",
        workout_plans
    )
    conn.commit()

    cursor.execute("SELECT id, professional_id FROM custom_workout_plans ORDER BY id")
    wp_ids = [r['id'] for r in cursor.fetchall()]

    cursor.execute("SELECT id, professional_id FROM professional_workouts ORDER BY id")
    pw_map = cursor.fetchall()
    alex_ex = [e['id'] for e in pw_map if e['professional_id'] == 1]
    mike_ex = [e['id'] for e in pw_map if e['professional_id'] == 3]

    def assign_exercises(plan_id, ex_ids, days):
        for day, eid in zip(days, ex_ids):
            cursor.execute(
                "INSERT INTO custom_workout_plan_exercises (plan_id,workout_day,workout_id) VALUES (%s,%s,%s)",
                (plan_id, day, eid)
            )

    if wp_ids and alex_ex:
        assign_exercises(wp_ids[0], alex_ex[:3], ['Monday','Wednesday','Friday'])
        if len(alex_ex) > 3:
            assign_exercises(wp_ids[0], alex_ex[3:], ['Tuesday','Thursday'])
    if len(wp_ids) > 1 and mike_ex:
        assign_exercises(wp_ids[1], mike_ex[:4], ['Monday','Tuesday','Thursday','Friday'])
    if len(wp_ids) > 2 and mike_ex:
        assign_exercises(wp_ids[2], mike_ex[2:5], ['Monday','Wednesday','Saturday'])
    conn.commit()

    # ─────────────────────────────────────────────
    # 10. TRANSFORMATIONS
    # ─────────────────────────────────────────────
    print("Seeding transformations...")
    transformations = [
        (1, "Rohan K.",    95.0, 78.0, "12 weeks", "Lost 17kg in 12 weeks with our compound lifting program and calorie deficit.",      "", 5.0),
        (1, "Ananya M.",   72.0, 62.0, "8 weeks",  "Dropped 10kg and improved endurance significantly.",                               "", 4.8),
        (3, "Dev S.",      88.0, 72.0, "16 weeks", "Full body recomposition — lost fat, gained muscle simultaneously.",                  "", 5.0),
        (3, "Kavya R.",    65.0, 59.0, "10 weeks", "Lost 6kg while getting stronger. PRs improved across all lifts.",                   "", 4.9),
        (2, "Meera P.",    70.0, 62.0, "12 weeks", "Holistic diet transformation. Reversed PCOS symptoms through nutrition.",           "", 5.0),
        (4, "Ritesh J.",   82.0, 74.0, "8 weeks",  "30-day HIIT program followed by 4 weeks strength. Total 8kg lost.",               "", 4.5),
    ]
    cursor.executemany(
        "INSERT INTO transformations (professional_id,client_name,before_weight,after_weight,duration,description,image,rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        transformations
    )
    conn.commit()

    # ─────────────────────────────────────────────
    # 11. PROFESSIONAL REVIEWS
    # ─────────────────────────────────────────────
    print("Seeding reviews...")
    reviews = [
        (1, 2, 5.0, "Alex completely changed my lifestyle. His workout plans are intense but achievable. Lost 10kg!"),
        (1, 3, 4.5, "Great trainer. Very knowledgeable about nutrition too. Would recommend."),
        (2, 4, 5.0, "Sarah saved my life. Her diet plans are delicious AND effective. PCOS under control now!"),
        (2, 6, 4.8, "Best dietician I've ever worked with. The vegan plan she made is amazing."),
        (3, 3, 5.0, "Mike is on another level. He handles both my training AND diet. Incredible results!"),
        (3, 5, 5.0, "The complete package. Mike's program gave me the body recomp I was chasing for 2 years."),
        (4, 2, 4.0, "Emma's HIIT sessions are brutal but effective. Great for cardio improvement."),
    ]
    cursor.executemany(
        "INSERT INTO professional_reviews (professional_id,user_id,rating,review_text) VALUES (%s,%s,%s,%s)",
        reviews
    )
    conn.commit()

    # ─────────────────────────────────────────────
    # 12. NOTIFICATIONS
    # ─────────────────────────────────────────────
    print("Seeding notifications...")
    notifications = [
        # for Alex (prof_id=1)
        (None, 1, "hire_request", "New hire request from Harsh Pandya — Basic Training plan.", False),
        (None, 1, "payment",      "Payment of ₹2,000 received from Harsh Pandya.",             True),
        (None, 1, "review",       "Harsh Pandya left you a 5-star review!",                    False),
        # for Sarah (prof_id=2)
        (None, 2, "hire_request", "New hire request from Priya Verma — Diet Plan Basic.",      False),
        (None, 2, "payment",      "Payment of ₹1,500 received from Priya Verma.",              True),
        (None, 2, "hire_request", "New hire request from Neha Gupta — Diet Plan Premium.",     False),
        (None, 2, "payment",      "Payment of ₹4,000 received from Neha Gupta.",               True),
        # for Mike (prof_id=3)
        (None, 3, "hire_request", "New hire request from Rahul Sharma — Complete Transformation.", False),
        (None, 3, "payment",      "Payment of ₹8,000 received from Rahul Sharma.",             True),
        (None, 3, "review",       "Rahul Sharma left you a 4.5-star review!",                  False),
        (None, 3, "review",       "Arjun Singh left you a 5-star review!",                     False),
    ]
    cursor.executemany(
        "INSERT INTO notifications (user_id,professional_id,notification_type,message,is_read) VALUES (%s,%s,%s,%s,%s)",
        notifications
    )
    conn.commit()

    # ─────────────────────────────────────────────
    # 13. PROGRESS LOGS (multiple dates)
    # ─────────────────────────────────────────────
    print("Seeding progress logs...")
    for uid, start_w, end_w in [(2, 82, 78), (3, 95, 92), (4, 58, 56), (5, 70, 71), (6, 55, 53)]:
        for i, offset in enumerate([30, 20, 10, 0]):
            log_date = today - datetime.timedelta(days=offset)
            w = round(start_w + (end_w - start_w) * (3 - i) / 3, 1)
            try:
                cursor.execute("INSERT INTO progress_logs (user_id,weight_kg,log_date) VALUES (%s,%s,%s)", (uid, w, log_date))
            except:
                pass
    conn.commit()

    print("[OK] Seed complete! Test accounts:")
    print("="*50)
    print("ADMIN:    admin@goalfit.ai      / admin123")
    print("USER 1:   harsh@goalfit.ai     / password123  (client of Alex)")
    print("USER 2:   rahul@test.com       / password123  (client of Mike)")
    print("USER 3:   priya@test.com       / password123  (client of Sarah)")
    print("USER 4:   arjun@test.com       / password123  (client of Mike)")
    print("USER 5:   neha@test.com        / password123  (client of Sarah)")
    print("-"*50)
    print("TRAINER:  alex@trainer.com     / password123  (has clients + plans + reviews)")
    print("DIETICIAN:sarah@dietician.com  / password123  (has clients + diet plans + reviews)")
    print("BOTH:     mike@trainer.com     / password123  (has clients + full plans + reviews)")
    print("TRAINER:  emma@dietician.com   / password123  (has clients + transformations)")
    print("DIETICIAN:john@health.com      / password123")
    print("="*50)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed()
