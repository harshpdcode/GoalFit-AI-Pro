import os
import sys
import pandas as pd
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

# Excel files location
DOWNLOADS_DIR = r'C:\Users\harsh\Downloads'
EXCEL_FILES = [
    os.path.join(DOWNLOADS_DIR, 'Indian_NonVeg_Meals_Phase1.xlsx'),
    os.path.join(DOWNLOADS_DIR, 'Indian_Veg_Meals_Phase1.xlsx'),
    os.path.join(DOWNLOADS_DIR, 'Indian_Vegan_Meals_Phase1.xlsx'),
    os.path.join(DOWNLOADS_DIR, 'Indian_Eggetarian_Meals_Phase1.xlsx'),
    os.path.join(DOWNLOADS_DIR, 'Indian_Keto_Meals_Phase1.xlsx'),
    os.path.join(DOWNLOADS_DIR, 'GoalFit_AI_Pro_Diet_Meals_Dataset.xlsx')
]

def load_and_clean_data():
    print("[+] Loading Excel files...")
    dfs = []
    for filepath in EXCEL_FILES:
        if os.path.exists(filepath):
            try:
                df = pd.read_excel(filepath)
                df['source_file'] = os.path.basename(filepath)
                dfs.append(df)
                print(f"  - Loaded {os.path.basename(filepath)} ({len(df)} rows)")
            except Exception as e:
                print(f"  x Error reading {filepath}: {e}")
        else:
            print(f"  ! File not found: {filepath}")

    if not dfs:
        raise ValueError("No Excel files found!")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\n[+] Total combined records before cleaning: {len(combined)}")

    # Data Cleaning & Normalization
    combined['meal_name'] = combined['meal_name'].astype(str).str.strip()
    
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

    combined['meal_time'] = combined['meal_time'].apply(normalize_meal_time)

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

    combined['diet_type'] = combined['diet_type'].apply(normalize_diet_type)

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

    combined['goal_type'] = combined['goal_type'].apply(normalize_goal_type)

    # Numeric cleaning
    combined['calories'] = pd.to_numeric(combined['calories'], errors='coerce').fillna(300).astype(int)
    combined['proteins'] = pd.to_numeric(combined['proteins'], errors='coerce').fillna(10.0).astype(float)
    combined['carbs'] = pd.to_numeric(combined['carbs'], errors='coerce').fillna(30.0).astype(float)
    combined['fats'] = pd.to_numeric(combined['fats'], errors='coerce').fillna(8.0).astype(float)
    combined['option_group'] = pd.to_numeric(combined['option_group'], errors='coerce').fillna(1).astype(int)

    # Image src cleaning
    combined['img_src'] = combined['img_src'].fillna('static/images/diet/default_meal.jpg').astype(str).str.strip()

    # Deduplicate by meal_name, meal_time, diet_type, goal_type
    combined_dedup = combined.drop_duplicates(subset=['meal_name', 'meal_time', 'diet_type', 'goal_type'], keep='first')
    print(f"[+] Cleaned & Deduplicated unique meals: {len(combined_dedup)} records")

    return combined_dedup

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
