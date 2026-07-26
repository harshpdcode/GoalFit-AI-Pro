import os
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

def get_db_connection():
    """
    Creates and returns a MySQL database connection.
    Supports:
    1. Render / Cloud single DATABASE_URL / MYSQL_URL connection string (e.g., mysql://user:pass@host:3306/dbname)
    2. Individual environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
    3. Fallback to default local MySQL development settings
    """
    try:
        # Check if a unified DATABASE_URL or MYSQL_URL is provided by Cloud Provider
        db_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
        
        if db_url:
            # Parse connection parameters from URL string
            parsed = urlparse(db_url)
            host = parsed.hostname or "localhost"
            user = parsed.username or "root"
            password = parsed.password or ""
            database = parsed.path.lstrip('/') or "goalfit_ai"
            port = parsed.port or 3306
        else:
            # Read individual environment variables with backward-compatible defaults
            host = os.getenv("DB_HOST", "localhost")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "hmpandya528@")
            database = os.getenv("DB_NAME", "goalfit_ai")
            port = int(os.getenv("DB_PORT", 3306))

        # Additional SSL configuration if required by Cloud MySQL host
        ssl_ca = os.getenv("DB_SSL_CA")
        connect_kwargs = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "autocommit": True
        }
        
        if ssl_ca:
            connect_kwargs["ssl_ca"] = ssl_ca

        connection = mysql.connector.connect(**connect_kwargs)
        print("Database connected successfully!")
        return connection

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None