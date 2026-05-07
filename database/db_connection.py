import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "hmpandya528@"),
            database="goalfit_ai",
            autocommit=True   # IMPORTANT
        )

        print("Database connected successfully!")
        return connection

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None