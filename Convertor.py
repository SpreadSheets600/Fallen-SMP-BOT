import os
import sqlite3
import mysql.connector as mysql
from mysql.connector import Error

# SQLite Database Connection
sqlite_conn = sqlite3.connect('Version 1/User.db')  # Update with your SQLite DB path
sqlite_cursor = sqlite_conn.cursor()

from dotenv import *
load_dotenv()

# MySQL Database Connection
mysql_conn = mysql.connect(
            host=os.getenv("DB_HOST"),
            port=3306,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )

mysql_cursor = mysql_conn.cursor()

try:
    # Fetch data from SQLite
    sqlite_cursor.execute("SELECT * FROM user_data")  # Replace with your table name
    rows = sqlite_cursor.fetchall()

    # Insert data into MySQL
    for row in rows:
        discord_user_id = row[1]
        minecraft_username = row[2]
        character_name = row[3]  # Unused in MySQL, but you might want to use it elsewhere
        character_gender = row[4]
        character_backstory = row[5]
        timestamp = row[6]

        insert_query = """
        INSERT INTO Users (ID, Username, Gender, Backstory, Timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(insert_query, (
            discord_user_id,
            minecraft_username,
            character_gender,
            character_backstory,
            timestamp,
        ))

    # Commit the transaction
    mysql_conn.commit()
    print(f"Successfully transferred {len(rows)} records from SQLite to MySQL.")

except Error as e:
    print(f"Error occurred: {e}")

finally:
    # Close connections
    sqlite_cursor.close()
    sqlite_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
