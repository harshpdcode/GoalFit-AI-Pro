import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

from database.db_connection import get_db_connection

try:
    conn = get_db_connection()
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
