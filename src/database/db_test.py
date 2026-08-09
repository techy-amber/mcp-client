import os

import mysql.connector
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


connection = None

try:
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )

    if connection.is_connected():
        print("Connected to MySQL successfully!")

        cursor = connection.cursor()

        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()

        print("MySQL version:", version[0])

        cursor.close()

except mysql.connector.Error as error:
    print("MySQL connection failed:")
    print(error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")