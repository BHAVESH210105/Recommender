import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from your .env file.")

client = None

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=10000,
    )

    print("Checking MongoDB Atlas server status...")

    # Display the server information discovered by PyMongo.
    print("\nDiscovered servers:")

    for address, description in client.topology_description.server_descriptions().items():
        print(f"\nAddress: {address}")
        print(f"Server type: {description.server_type_name}")
        print(f"Error: {description.error}")

    # Test the connection.
    print("\nTesting MongoDB connection...")
    client.admin.command("ping")

    print("Successfully connected to MongoDB Atlas!")

    db_name = os.getenv("MONGO_DB_NAME", "cinematch")
    db = client[db_name]

    print(f"Database selected: {db.name}")
    print("Collections:", db.list_collection_names())

except Exception as error:
    print("\nConnection failed.")
    print(type(error).__name__, error)

finally:
    if client is not None:
        client.close()