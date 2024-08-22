import os
from pymongo import MongoClient

# Replace this with your MongoDB connection string
connection_string = os.getenv("MONGO_URI")

# Create a MongoClient instance
client = MongoClient(connection_string)

# List all the databases
print(client.list_database_names())

