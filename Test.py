import mysql.connector
from mysql.connector import errorcode

# Define source and target database connection details
source_db_config = {
    "host": "13.235.98.89",
    "port": 3306,
    "user": "u8231_fUqw1na6tk",
    "password": "=2i.jjP@d2C!dJQbiNfK1H.J",
    "database": "s8231_LoginSequrity",
}

target_db_config = {
    "host": "in4-b.potenfyr.in",
    "port": 3306,
    "user": "u67_hl2R7Dj8as",
    "password": "El3Ks6bYNGnFz6h.FZTv8!vd",
    "database": "s67_LoginSequrity",
}

# Connect to the source database
try:
    source_conn = mysql.connector.connect(**source_db_config)
    source_cursor = source_conn.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the source username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Source database does not exist")
    else:
        print(err)
    exit(1)

# Connect to the target database
try:
    target_conn = mysql.connector.connect(**target_db_config)
    target_cursor = target_conn.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the target username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Target database does not exist")
    else:
        print(err)
    exit(1)

# Get the list of tables from the source database
source_cursor.execute("SHOW TABLES")
tables = source_cursor.fetchall()

for (table_name,) in tables:
    # Dump the structure and data of each table from the source database
    source_cursor.execute(f"SHOW CREATE TABLE {table_name}")
    create_table_query = source_cursor.fetchone()[1]

    # Create the table in the target database
    target_cursor.execute(create_table_query)

    # Fetch all data from the source table
    source_cursor.execute(f"SELECT * FROM {table_name}")
    rows = source_cursor.fetchall()

    # Get column names to insert data
    columns = [i[0] for i in source_cursor.description]
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

    # Insert data into the target table
    target_cursor.executemany(insert_query, rows)

    # Commit changes to the target database
    target_conn.commit()

# Close the connections
source_cursor.close()
source_conn.close()
target_cursor.close()
target_conn.close()

print("Data transfer completed successfully.")
