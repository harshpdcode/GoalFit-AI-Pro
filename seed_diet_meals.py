import os
import sys
import pandas as pd
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Excel files location
DOWNLOADS_DIR = r'C:\Users\harsh\Downloads'
COMBINED_FILE = os.path.join(DOWNLOADS_DIR, 'Combined_Indian_Meals_Dataset.xlsx')
JSON_SEED_FILE = os.path.join(os.path.dirname(__file__), 'database', 'diet_meals_seed.json')

def load_and_clean_data():
    print("[+] Loading Curated Indian Meals Dataset...")
    
    if os.path.exists(COMBINED_FILE):
        df = pd.read_excel(COMBINED_FILE)
        print(f"  - Loaded {os.path.basename(COMBINED_FILE)} ({len(df)} rows)")
        
        column_mapping = {
            'Meal Name': 'meal_name',
            'Meal Time': 'meal_time',
            'Calories': 'calories',
            'Protein (g)': 'proteins',
            'Carbs (g)': 'carbs',
            'Fats (g)': 'fats',
            'Diet Type': 'diet_type',
            'Goal Type': 'goal_type',
            'Option Group': 'option_group',
            'Image Path': 'img_src'
        }
        df = df.rename(columns=column_mapping)
    elif os.path.exists(JSON_SEED_FILE):
        df = pd.read_json(JSON_SEED_FILE)
        print(f"  - Loaded {os.path.basename(JSON_SEED_FILE)} ({len(df)} rows)")
    else:
        raise ValueError("Dataset file not found!")

    # Data Cleaning & Normalization
    df['meal_name'] = df['meal_name'].astype(str).str.strip()
    
    # Meal time normalization
    def normalize_meal_time(val):
        val_str = str(val).strip().lower()
        if 'breakfast' in val_str:
            return 'Breakfast'
        elif 'lunch' in val_str:
            return 'Lunch'
        elif 'dinner' in val_str:
            return 'Dinner'
        elif 'snack' in val_str:
            return 'Snack'
        return 'Breakfast'

    df['meal_time'] = df['meal_time'].apply(normalize_meal_time)

    # Diet type normalization
    def normalize_diet_type(val):
        val_str = str(val).strip().lower()
        if 'non' in val_str:
            return 'Non-Veg'
        elif 'vegan' in val_str:
            return 'Vegan'
        elif 'egg' in val_str:
            return 'Eggetarian'
        elif 'keto' in val_str:
            return 'Keto'
        elif 'veg' in val_str:
            return 'Veg'
        return 'Veg'

    df['diet_type'] = df['diet_type'].apply(normalize_diet_type)

    # Goal type normalization
    def normalize_goal_type(val):
        val_str = str(val).strip().lower()
        if 'loss' in val_str:
            return 'Weight Loss'
        elif 'gain' in val_str or 'muscle' in val_str:
            return 'Muscle Gain'
        elif 'maintain' in val_str:
            return 'Maintenance'
        return 'Weight Loss'

    df['goal_type'] = df['goal_type'].apply(normalize_goal_type)

    # Numeric cleaning
    df['calories'] = pd.to_numeric(df['calories'], errors='coerce').fillna(300).astype(int)
    df['proteins'] = pd.to_numeric(df['proteins'], errors='coerce').fillna(10.0).astype(float)
    df['carbs'] = pd.to_numeric(df['carbs'], errors='coerce').fillna(30.0).astype(float)
    df['fats'] = pd.to_numeric(df['fats'], errors='coerce').fillna(8.0).astype(float)
    df['option_group'] = pd.to_numeric(df['option_group'], errors='coerce').fillna(1).astype(int)

    # Image src cleaning
    df['img_src'] = df['img_src'].fillna('static/images/diet/salad.jpeg').astype(str).str.strip()

    print(f"[+] Cleaned dataset: {len(df)} records")

    return df

def insert_to_db(connection_target="local", custom_db_url=None):
    df_meals = load_and_clean_data()
    
    print(f"\n[+] Connecting to MySQL Target: [{connection_target}]...")
    
    try:
        if custom_db_url or connection_target == "railway":
            db_url = custom_db_url or os.getenv("RAILWAY_MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
            if not db_url:
                print("x Railway / Remote Database URL not specified in env!")
                print("  Set RAILWAY_MYSQL_URL or DATABASE_URL in .env or pass URL parameter.")
                return
            parsed = urlparse(db_url)
            conn = mysql.connector.connect(
                host=parsed.hostname or "localhost",
                user=parsed.username or "root",
                password=parsed.password or "",
                database=parsed.path.lstrip('/') or "goalfit_ai",
                port=parsed.port or 3306,
                autocommit=True
            )
        else:
            host = os.getenv("DB_HOST", "localhost")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "hmpandya528@")
            database = os.getenv("DB_NAME", "goalfit_ai")
            port = int(os.getenv("DB_PORT", 3306))
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                autocommit=True
            )
            
        cursor = conn.cursor()
        print(f"[+] Connected to MySQL database!")

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_meals (
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

        insert_query = """
        INSERT INTO diet_meals (meal_name, meal_time, calories, proteins, carbs, fats, diet_type, goal_type, option_group, img_src)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Truncate to refresh with 100% clean dataset
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE diet_meals;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("[+] Reset existing diet_meals table.")

        # Batch Insertion
        batch_size = 500
        records = []
        for _, row in df_meals.iterrows():
            records.append((
                str(row['meal_name'])[:100],
                str(row['meal_time'])[:50],
                int(row['calories']),
                float(row['proteins']),
                float(row['carbs']),
                float(row['fats']),
                str(row['diet_type'])[:50],
                str(row['goal_type'])[:50],
                int(row['option_group']),
                str(row['img_src'])[:255]
            ))

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            cursor.executemany(insert_query, batch)
            print(f"  -> Inserted {i + len(batch)} / {len(records)} meals...")

        cursor.execute("SELECT COUNT(*) FROM diet_meals;")
        count = cursor.fetchone()[0]
        print(f"\n[SUCCESS] Total meals in diet_meals [{connection_target}]: {count}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"x Database Insertion Error: {e}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "local"
    url = sys.argv[2] if len(sys.argv) > 2 else None
    insert_to_db(connection_target=target, custom_db_url=url)
