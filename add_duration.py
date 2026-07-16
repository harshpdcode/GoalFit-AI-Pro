import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "hmpandya528@"),
        database="goalfit_ai"
    )
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE transformations ADD COLUMN duration VARCHAR(50);")
    conn.commit()
    print("Successfully added duration column to transformations table.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
