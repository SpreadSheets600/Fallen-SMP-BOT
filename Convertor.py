import sqlite3

# Connect to SQLite
sqlite_conn = sqlite3.connect('User.db')
sqlite_cursor = sqlite_conn.cursor()

# Example table name
table_name = 'user_data'

# Fetch data from SQLite
sqlite_cursor.execute(f"SELECT * FROM {table_name}")
rows = sqlite_cursor.fetchall()

# Get column names
column_names = [description[0] for description in sqlite_cursor.description]

# Insert data into MongoDB
for row in rows:
    document = dict(zip(column_names, row))
    print(document)