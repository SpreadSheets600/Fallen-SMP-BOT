import mysql.connector as mysql
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connect(
            host="13.235.98.89",
            port="3306",
            user="u8231_sZntvftnWa",
            password="R77zhD+dKG!JiPmMkMJN^4QZ",
            database="s8231_Users",
        )

        cursor = connection.cursor()
        print("[ + ] Database Connection Established")
        return connection, cursor

    except Exception as e:
        print(f"[ - ] Error Connecting To Database : {e}")
        return None, None

connection, cursor = connect_to_database()

if connection and cursor:
    cursor.execute(
        "ALTER TABLE Users DROP COLUMN ID"
    )
    print("[ + ] Column Dropped")
    connection.commit()
    cursor.execute(
        "ALTER TABLE Users ADD COLUMN ID INT PRIMARY KEY"
    )
    connection.commit()
    print("[ + ] Column Added")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Users (ID INT PRIMARY KEY, Username VARCHAR(25), Gender VARCHAR(10), Backstory VARCHAR(3000), Timestamp VARCHAR(25))"
    )
    connection.commit()
    print("[ + ] Tables Created")