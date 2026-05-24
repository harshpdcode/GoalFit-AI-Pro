import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

def create_schema():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "hmpandya528@")
        )
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS goalfit_ai;")
        cursor.execute("USE goalfit_ai;")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = [
            "payments", "custom_workout_plan_exercises", "custom_workout_plans",
            "professional_workouts", "custom_diet_plan_meals", "custom_diet_plans",
            "professional_meals", "transformations", "client_assignments",
            "hire_requests", "professional_pricing", "professionals",
            "water_logs", "user_feedback", "activity_logs",
            "user_workouts", "user_meals", "workout_exercises",
            "diet_meals", "progress_logs", "step_recommendations", 
            "goal_predictions", "bmi_records", "user_health", "users",
            "chat_messages", "diet_logs", "progress_photos"
        ]
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # ===== USERS (with role) =====
        cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ===== USER HEALTH =====
        cursor.execute("""
        CREATE TABLE user_health (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            age INT,
            gender VARCHAR(20),
            height_cm FLOAT,
            weight_kg FLOAT,
            target_weight FLOAT,
            activity_level VARCHAR(50),
            goal_type VARCHAR(50),
            diet_preference VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===== BMI RECORDS =====
        cursor.execute("""
        CREATE TABLE bmi_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            bmi_value FLOAT,
            bmi_category VARCHAR(50),
            recorded_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===== GOAL PREDICTIONS =====
        cursor.execute("""
        CREATE TABLE goal_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            current_weight FLOAT,
            target_weight FLOAT,
            weekly_change_rate FLOAT,
            estimated_weeks INT,
            estimated_completion_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===== STEP RECOMMENDATIONS =====
        cursor.execute("""
        CREATE TABLE step_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            daily_steps INT,
            calories_to_burn INT,
            distance_km FLOAT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===== PROGRESS LOGS =====
        cursor.execute("""
        CREATE TABLE progress_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            weight_kg FLOAT,
            log_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===== WORKOUT EXERCISES =====
        cursor.execute("""
        CREATE TABLE workout_exercises (
            id INT AUTO_INCREMENT PRIMARY KEY,
            exercise_name VARCHAR(100),
            target_muscle VARCHAR(50),
            muscle_id INT,
            calories_burned INT,
            difficulty_level VARCHAR(50),
            option_group INT,
            img_src VARCHAR(255),
            video_src VARCHAR(255)
        );
        """)

        # ===== DIET MEALS =====
        cursor.execute("""
        CREATE TABLE diet_meals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            meal_name VARCHAR(100),
            meal_time VARCHAR(50),
            calories INT,
            proteins FLOAT,
            carbs FLOAT,
            fats FLOAT,
            diet_type VARCHAR(50),
            goal_type VARCHAR(50),
            option_group INT,
            img_src VARCHAR(255)
        );
        """)

        # ===== USER WORKOUTS =====
        cursor.execute("""
        CREATE TABLE user_workouts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            workout_id INT,
            performed_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (workout_id) REFERENCES workout_exercises(id) ON DELETE CASCADE
        );
        """)

        # ===== USER MEALS =====
        cursor.execute("""
        CREATE TABLE user_meals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            meal_id INT,
            meal_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES diet_meals(id) ON DELETE CASCADE
        );
        """)

        # ===== ACTIVITY LOGS =====
        cursor.execute("""
        CREATE TABLE activity_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(100),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """)



        # ===== WATER LOGS =====
        cursor.execute("""
        CREATE TABLE water_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            glasses INT DEFAULT 0,
            goal_glasses INT DEFAULT 8,
            log_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===========================
        # MARKETPLACE TABLES
        # ===========================
        cursor.execute("""
        CREATE TABLE professionals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            phone VARCHAR(20),
            role ENUM('trainer','dietician','both'),
            bio TEXT,
            experience_years INT,
            specialization VARCHAR(255),
            profile_photo VARCHAR(255) DEFAULT 'static/images/profile_img/default_prof.jpg',
            is_verified BOOLEAN DEFAULT FALSE,
            rating FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ===== USER FEEDBACK =====
        cursor.execute("""
        CREATE TABLE user_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT DEFAULT NULL,
            subject VARCHAR(200),
            message TEXT,
            status VARCHAR(20) DEFAULT 'unread',
            admin_reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE professional_pricing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            professional_id INT,
            plan_type VARCHAR(50),
            duration_days INT,
            price FLOAT,
            description TEXT,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE hire_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT,
            plan_type VARCHAR(50),
            goal_type VARCHAR(50),
            payment_status VARCHAR(50) DEFAULT 'pending',
            status ENUM('pending','accepted','rejected','completed') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE client_assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT,
            plan_type VARCHAR(50),
            start_date DATE,
            end_date DATE,
            status VARCHAR(50) DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE transformations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            professional_id INT,
            client_name VARCHAR(100),
            before_weight FLOAT,
            after_weight FLOAT,
            description TEXT,
            image VARCHAR(255),
            rating FLOAT,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE professional_meals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            professional_id INT,
            meal_name VARCHAR(100),
            calories INT,
            protein FLOAT,
            carbs FLOAT,
            fats FLOAT,
            ingredients TEXT,
            instructions TEXT,
            image VARCHAR(255),
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE custom_diet_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT,
            plan_name VARCHAR(100),
            goal VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE custom_diet_plan_meals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plan_id INT,
            meal_type VARCHAR(50),
            meal_id INT,
            FOREIGN KEY (plan_id) REFERENCES custom_diet_plans(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES professional_meals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE professional_workouts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            professional_id INT,
            workout_name VARCHAR(100),
            target_muscle VARCHAR(50),
            sets INT,
            reps INT,
            rest_time INT,
            instructions TEXT,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE custom_workout_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT,
            plan_name VARCHAR(100),
            goal VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE custom_workout_plan_exercises (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plan_id INT,
            workout_id INT,
            workout_day VARCHAR(50),
            FOREIGN KEY (plan_id) REFERENCES custom_workout_plans(id) ON DELETE CASCADE,
            FOREIGN KEY (workout_id) REFERENCES professional_workouts(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            professional_id INT,
            hire_request_id INT,
            razorpay_payment_id VARCHAR(100),
            amount FLOAT,
            commission_amount FLOAT,
            professional_amount FLOAT,
            payment_status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (professional_id) REFERENCES professionals(id) ON DELETE SET NULL,
            FOREIGN KEY (hire_request_id) REFERENCES hire_requests(id) ON DELETE SET NULL
        );
        """)

        # ===========================
        # NEW FEATURE TABLES
        # ===========================
        cursor.execute("""
        CREATE TABLE chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT,
            sender_role VARCHAR(20),
            receiver_id INT,
            receiver_role VARCHAR(20),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE diet_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            meal_id INT,
            log_date DATE,
            is_completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES diet_meals(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE progress_photos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            photo_path VARCHAR(255),
            log_date DATE,
            is_shared BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # ===========================
        # INSERT WORKOUT DATA
        # ===========================
        workout_data = [
            ("Push Ups", "Chest", 1, 50, "Beginner", 1, "static/images/workout/1.jpg", "https://www.youtube.com/embed/IODxDxX7oi4"),
            ("Knee Push Ups", "Chest", 1, 30, "Beginner", 2, "static/images/workout/2.jpg", ""),
            ("Dumbbell Press", "Chest", 1, 80, "Intermediate", 1, "static/images/workout/3.png", "https://www.youtube.com/embed/xCcEUAEkYvI"),
            ("Incline Press", "Chest", 1, 90, "Intermediate", 2, "static/images/workout/4.jpg", ""),
            ("Bench Press", "Chest", 1, 100, "Advanced", 1, "static/images/workout/5.jpg", "https://www.youtube.com/embed/rT7DgCr-3pg"),
            ("Cable Crossover", "Chest", 1, 95, "Advanced", 2, "static/images/workout/6.jpg", ""),
            
            ("Bodyweight Squats", "Legs", 2, 70, "Beginner", 1, "static/images/workout/7.jpg", "https://www.youtube.com/embed/gb2eB5r95A4"),
            ("Lunges", "Legs", 2, 60, "Beginner", 2, "static/images/workout/8.jpg", ""),
            ("Goblet Squats", "Legs", 2, 90, "Intermediate", 1, "static/images/workout/9.jpg", ""),
            ("Leg Press", "Legs", 2, 85, "Intermediate", 2, "static/images/workout/10.jpg", ""),
            ("Barbell Squats", "Legs", 2, 120, "Advanced", 1, "static/images/workout/11.jpg", ""),
            ("Deadlifts", "Legs", 2, 150, "Advanced", 2, "static/images/workout/12.jpg", ""),
            
            ("Plank", "Abs", 3, 30, "Beginner", 1, "static/images/workout/13.jpg", "https://www.youtube.com/embed/pSHjTRCQxIw"),
            ("Crunches", "Abs", 3, 25, "Beginner", 2, "static/images/workout/14.jpg", "https://www.youtube.com/embed/Xyd_fa5zoEU"),
            ("Bicycle Crunches", "Abs", 3, 40, "Intermediate", 1, "static/images/workout/15.jpg", "https://www.youtube.com/embed/9FGilxCbdz8"),
            ("Leg Raises", "Abs", 3, 45, "Intermediate", 2, "static/images/workout/16.png", "https://www.youtube.com/embed/l4kQd9eFSqk"),
            
            ("Jump Rope", "Cardio", 4, 120, "Beginner", 1, "static/images/workout/17.png", "https://www.youtube.com/embed/u3zgHI8QnqE"),
            ("Jumping Jacks", "Cardio", 4, 100, "Beginner", 2, "static/images/workout/18.png", "https://www.youtube.com/embed/iSSAk4XCsA8"),
            ("Running", "Cardio", 4, 200, "Intermediate", 1, "static/images/workout/4.jpg", "https://www.youtube.com/embed/5aJqM1sL1P8"),
            ("Cycling", "Cardio", 4, 180, "Intermediate", 2, "static/images/workout/5.jpg", "https://www.youtube.com/embed/gC_L9qAHVJ8")
        ]
        q = "INSERT INTO workout_exercises (exercise_name, target_muscle, muscle_id, calories_burned, difficulty_level, option_group, img_src, video_src) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q, workout_data)

        # ===========================
        # INSERT MEAL DATA
        # ===========================
        meal_data = [
            # VEGETARIAN Weight Loss
            ("Oatmeal Power Bowl", "Breakfast", 300, 10, 40, 5, "Vegetarian", "Weight Loss", 1, "static/images/diet/oats_ai.jpg"),
            ("Poha", "Breakfast", 250, 6, 45, 4, "Vegetarian", "Weight Loss", 2, "static/images/diet/salad.jpeg"),
            ("Quinoa Veg Bowl", "Lunch", 350, 15, 50, 8, "Vegetarian", "Weight Loss", 1, "static/images/diet/chickpeas.jpeg"),
            ("Brown Rice & Dal", "Lunch", 380, 18, 55, 6, "Vegetarian", "Weight Loss", 2, "static/images/diet/dal_rice_ai.png"),
            ("Grilled Paneer Salad", "Dinner", 400, 20, 15, 12, "Vegetarian", "Weight Loss", 1, "static/images/diet/paneer_salad_ai.png"),
            ("Veg Soup & Roti", "Dinner", 300, 8, 40, 5, "Vegetarian", "Weight Loss", 2, "static/images/diet/soup_and_roti.jpeg"),

            # VEGETARIAN Weight Gain
            ("Paneer Veg Sandwich", "Breakfast", 450, 20, 50, 15, "Vegetarian", "Weight Gain", 1, "static/images/diet/sandwich_ai.png"),
            ("Banana Paratha", "Breakfast", 400, 10, 60, 12, "Vegetarian", "Weight Gain", 2, "static/images/diet/roti_ai.png"),
            ("Paneer Butter Masala & Roti", "Lunch", 600, 22, 65, 20, "Vegetarian", "Weight Gain", 1, "static/images/diet/grilled_paneer_salad.jpeg"),
            ("Soyabean Curry & Rice", "Lunch", 550, 25, 70, 15, "Vegetarian", "Weight Gain", 2, "static/images/diet/dal_rise.jpeg"),
            ("Dal Makhani & Naan", "Dinner", 650, 18, 80, 25, "Vegetarian", "Weight Gain", 1, "static/images/diet/dal_rice_ai.png"),
            ("Mix Veg Cheese Bake", "Dinner", 550, 16, 50, 22, "Vegetarian", "Weight Gain", 2, "static/images/diet/salad.jpeg"),

            # NON-VEGETARIAN Weight Loss
            ("Eggs & Whole Wheat Toast", "Breakfast", 320, 18, 30, 10, "Non-Vegetarian", "Weight Loss", 1, "static/images/diet/sandwich_ai.png"),
            ("Omelette with Spinach", "Breakfast", 280, 20, 10, 12, "Non-Vegetarian", "Weight Loss", 2, "static/images/diet/salad.jpeg"),
            ("Grilled Chicken Salad", "Lunch", 350, 40, 15, 15, "Non-Vegetarian", "Weight Loss", 1, "static/images/diet/chickpeas.jpeg"),
            ("Tuna & Quinoa", "Lunch", 360, 35, 40, 5, "Non-Vegetarian", "Weight Loss", 2, "static/images/diet/apple_slice.jpeg"),
            ("Baked Salmon & Veggies", "Dinner", 400, 30, 20, 18, "Non-Vegetarian", "Weight Loss", 1, "static/images/diet/grilled_paneer_salad.jpeg"),
            ("Chicken Clear Soup", "Dinner", 250, 25, 5, 8, "Non-Vegetarian", "Weight Loss", 2, "static/images/diet/soup_and_roti.jpeg"),

            # NON-VEGETARIAN Weight Gain
            ("Chicken Sausage & Eggs", "Breakfast", 500, 30, 20, 25, "Non-Vegetarian", "Weight Gain", 1, "static/images/diet/sandwich_ai.png"),
            ("Steak & Potato Hash", "Breakfast", 600, 35, 50, 25, "Non-Vegetarian", "Weight Gain", 2, "static/images/diet/salad.jpeg"),
            ("Chicken Tikka Masala & Rice", "Lunch", 700, 45, 80, 25, "Non-Vegetarian", "Weight Gain", 1, "static/images/diet/dal_rice_ai.png"),
            ("Mutton Curry & Paratha", "Lunch", 750, 40, 60, 35, "Non-Vegetarian", "Weight Gain", 2, "static/images/diet/roti_ai.png"),
            ("Grilled Steak & Sweet Potato", "Dinner", 650, 50, 55, 20, "Non-Vegetarian", "Weight Gain", 1, "static/images/diet/grilled_paneer_salad.jpeg"),
            ("Fish Curry with Brown Rice", "Dinner", 600, 35, 70, 15, "Non-Vegetarian", "Weight Gain", 2, "static/images/diet/dal_rise.jpeg"),

            # VEGAN Weight Loss
            ("Fruit Smoothie & Chia", "Breakfast", 250, 8, 40, 5, "Vegan", "Weight Loss", 1, "static/images/diet/apple_slice.jpeg"),
            ("Avocado Toast", "Breakfast", 300, 6, 35, 12, "Vegan", "Weight Loss", 2, "static/images/diet/sandwich.jpeg"),
            ("Tofu Salad", "Lunch", 300, 20, 20, 15, "Vegan", "Weight Loss", 1, "static/images/diet/salad.jpeg"),
            ("Lentil Soup", "Lunch", 280, 15, 40, 5, "Vegan", "Weight Loss", 2, "static/images/diet/soup_and_roti.jpeg"),
            ("Stir-fry Veg & Tofu", "Dinner", 350, 22, 25, 12, "Vegan", "Weight Loss", 1, "static/images/diet/chickpeas.jpeg"),
            ("Zucchini Noodles & Tomato", "Dinner", 200, 5, 25, 5, "Vegan", "Weight Loss", 2, "static/images/diet/salad.jpeg"),

            # VEGAN Weight Gain
            ("Peanut Butter Toast & Shake", "Breakfast", 500, 15, 60, 20, "Vegan", "Weight Gain", 1, "static/images/diet/sandwich.jpeg"),
            ("Oats with Nuts & Dates", "Breakfast", 450, 12, 70, 15, "Vegan", "Weight Gain", 2, "static/images/diet/oats_ai.jpg"),
            ("Chickpea Curry & Rice", "Lunch", 600, 20, 85, 15, "Vegan", "Weight Gain", 1, "static/images/diet/chickpeas.jpeg"),
            ("Vegan Burger & Fries", "Lunch", 650, 18, 90, 25, "Vegan", "Weight Gain", 2, "static/images/diet/sandwich_ai.png"),
            ("Sweet Potato & Black Bean Bowl", "Dinner", 550, 15, 80, 10, "Vegan", "Weight Gain", 1, "static/images/diet/salad.jpeg"),
            ("Mushroom Risotto (Vegan)", "Dinner", 500, 12, 75, 18, "Vegan", "Weight Gain", 2, "static/images/diet/dal_rise.jpeg"),
            
            # SNACKS (Generic)
            ("Roasted Chickpeas", "snacks", 150, 8, 20, 4, "Vegetarian", "Weight Loss", 1, "static/images/diet/chickpeas.jpeg"),
            ("Fruit & Nut Mix", "snacks", 200, 5, 25, 10, "Vegan", "Weight Gain", 1, "static/images/diet/apple_slice.jpeg"),
            ("Boiled Eggs", "snacks", 140, 12, 1, 10, "Non-Vegetarian", "Weight Loss", 1, "static/images/diet/sandwich_ai.png"),
            ("Protein Bar", "snacks", 250, 20, 30, 8, "Vegetarian", "Weight Gain", 2, "static/images/diet/salad.jpeg")
        ]
        q2 = "INSERT INTO diet_meals (meal_name, meal_time, calories, proteins, carbs, fats, diet_type, goal_type, option_group, img_src) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q2, meal_data)

        # ===========================
        # SEED ADMIN USER
        # ===========================
        admin_password = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO users (id, name, email, password, role) 
            VALUES (1, 'Admin', 'admin@goalfit.ai', %s, 'admin')
        """, (admin_password,))

        # ===========================
        # SEED REGULAR USER
        # ===========================
        user_password = generate_password_hash("password123")
        cursor.execute("""
            INSERT INTO users (id, name, email, password, role) 
            VALUES (2, 'Test User', 'user@test.com', %s, 'user')
        """, (user_password,))
        cursor.execute("INSERT INTO user_health (user_id, age, gender, height_cm, weight_kg, target_weight, activity_level, goal_type, diet_preference) VALUES (2, 23, 'Male', 175, 82, 72, 'Moderate', 'Weight Loss', 'Vegetarian')")
        cursor.execute("INSERT INTO bmi_records (user_id, bmi_value, bmi_category, recorded_date) VALUES (2, 26.8, 'Overweight', '2026-01-15')")
        cursor.execute("INSERT INTO progress_logs (user_id, weight_kg, log_date) VALUES (2, 82, '2026-01-15')")
        cursor.execute("INSERT INTO goal_predictions (user_id, current_weight, target_weight, weekly_change_rate, estimated_weeks, estimated_completion_date) VALUES (2, 82, 72, 0.8, 12, '2026-05-20')")
        cursor.execute("INSERT INTO step_recommendations (user_id, daily_steps, calories_to_burn, distance_km) VALUES (2, 8000, 320, 6.2)")

        # Seed activity log
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (1, 'system_setup', 'Database initialized with seed data')")

        # ===========================
        # SEED PROFESSIONALS & CLIENTS
        # ===========================
        prof_pass = generate_password_hash("password123")
        prof_data = [
            (1, "Alex Trainer", "alex@trainer.com", prof_pass, "9876543210", "trainer", "Elite personal trainer specializing in weight loss and bodybuilding.", 5, "Weight Loss, Muscle Building", True, 4.8),
            (2, "Sarah Dietician", "sarah@dietician.com", prof_pass, "9876543211", "dietician", "Certified clinical nutritionist with a focus on holistic health.", 8, "Vegan Diets, PCOS, Weight Loss", True, 4.9),
            (3, "Mike Hybrid", "mike@trainer.com", prof_pass, "9876543212", "both", "Complete transformation coach. I handle both your lifting and your kitchen.", 10, "Body Recomposition", True, 5.0),
            (4, "Emma Coach", "emma@dietician.com", prof_pass, "9876543213", "trainer", "HIIT and mobility expert.", 3, "HIIT, Yoga", False, 4.2),
            (5, "Dr. John", "john@health.com", prof_pass, "9876543214", "dietician", "Expert in sports nutrition.", 12, "Sports Nutrition", True, 4.7)
        ]
        cursor.executemany("""
            INSERT INTO professionals (id, full_name, email, password, phone, role, bio, experience_years, specialization, is_verified, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, prof_data)

        pricing_data = [
            (1, 1, 'Basic Training', 30, 2000, '4 weeks of personalized workout routines.'),
            (2, 2, 'Diet Plan', 30, 1500, 'Customized diet plan with weekly check-ins.'),
            (3, 3, 'Complete Transformation', 90, 8000, '90 days of complete workout and diet coaching.')
        ]
        cursor.executemany("INSERT INTO professional_pricing (id, professional_id, plan_type, duration_days, price, description) VALUES (%s,%s,%s,%s,%s,%s)", pricing_data)

        # Additional Mock Users
        test_users = [
            (3, "Test User 1", "test1@goalfit.ai", user_password, "user"),
            (4, "Test User 2", "test2@goalfit.ai", user_password, "user"),
            (5, "Test User 3", "test3@goalfit.ai", user_password, "user"),
            (6, "Test User 4", "test4@goalfit.ai", user_password, "user")
        ]
        cursor.executemany("INSERT INTO users (id, name, email, password, role) VALUES (%s,%s,%s,%s,%s)", test_users)

        # Simulate Client Assignments (Harsh -> Alex Trainer, Test User 1 -> Mike Hybrid)
        cursor.execute("INSERT INTO client_assignments (user_id, professional_id, plan_type, start_date, end_date, status) VALUES (2, 1, 'Basic Training', '2026-05-01', '2026-06-01', 'active')")
        cursor.execute("INSERT INTO client_assignments (user_id, professional_id, plan_type, start_date, end_date, status) VALUES (3, 3, 'Complete Transformation', '2026-04-15', '2026-07-15', 'active')")

        # Simulate payments
        cursor.execute("INSERT INTO hire_requests (id, user_id, professional_id, plan_type, payment_status, status) VALUES (1, 2, 1, 'Basic Training', 'paid', 'accepted')")
        cursor.execute("INSERT INTO hire_requests (id, user_id, professional_id, plan_type, payment_status, status) VALUES (2, 3, 3, 'Complete Transformation', 'paid', 'accepted')")
        cursor.execute("INSERT INTO payments (user_id, professional_id, hire_request_id, razorpay_payment_id, amount, commission_amount, professional_amount, payment_status) VALUES (2, 1, 1, 'pay_mock1', 2000, 300, 1700, 'paid')")
        cursor.execute("INSERT INTO payments (user_id, professional_id, hire_request_id, razorpay_payment_id, amount, commission_amount, professional_amount, payment_status) VALUES (3, 3, 2, 'pay_mock2', 8000, 1200, 6800, 'paid')")


        conn.commit()
        print("Success: Database setup completed successfully!")
        print("Admin Login: admin@goalfit.ai / admin123")
        print("User Login: user@test.com / password123")
        print("Professional Logins: (e.g. mike@trainer.com / password123)")

    except mysql.connector.Error as err:
        print(f"Error during setup: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

if __name__ == "__main__":
    create_schema()
