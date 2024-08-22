import os
import mysql.connector as mysql
from pymongo import MongoClient

# Load environment variables
mongo_connection_string = "NAH"
mysql_host = "DB_HOST"
mysql_user = "DB_USER"
mysql_password = "DB_PASS"
mysql_database = "DB_NAME"

# Print environment variables for debugging (remove in production)
print(f"Mongo URI: {mongo_connection_string}")
print(f"MySQL Host: {mysql_host}")
print(f"MySQL User: {mysql_user}")

# Connect to MySQL
try:
    mysql_conn = mysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    print("MySQL connection successful")
except mysql.Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit(1)

# Connect to MongoDB
try:
    mongo_client = MongoClient(mongo_connection_string)
    mongo_db = mongo_client['Users']  # Change as needed
    mongo_collection = mongo_db['UserData']  # Change as needed
    print("MongoDB connection successful")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Fetch data from MySQL
try:
    mysql_cursor.execute("SELECT * FROM Users")  # Replace 'your_table' with the actual table name
    rows = mysql_cursor.fetchall()
    if rows:
        mongo_collection.insert_many(rows)
        print(f"Inserted {len(rows)} documents into MongoDB")
    else:
        print("No data found in MySQL")
except mysql.Error as e:
    print(f"Error fetching data from MySQL: {e}")
except Exception as e:
    print(f"Error inserting data into MongoDB: {e}")

# Close connections
finally:
    if mysql_cursor:
        mysql_cursor.close()
    if mysql_conn:
        mysql_conn.close()
    if mongo_client:
        mongo_client.close()
