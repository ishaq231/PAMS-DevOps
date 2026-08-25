"""
24030388 - Ishaq Modassir Mushtaq

Database connection and pooling utilities.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class Database_connection:
    """Simple database connection wrapper."""

    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            print("Connected to the database successfully!")
        except Error as e:
            print(f"Error while connecting to the database: {e}")
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    db = Database_connection()
    conn = db.connect()
    db.close()