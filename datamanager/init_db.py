import sqlite3

# Path to your SQLite database file
DB_PATH = "database.db"
SCHEMA_PATH = "datamanager/schema.sql"

# Read the schema.sql file
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema_sql = f.read()

# Connect to the database and execute the schema
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.executescript(schema_sql)
conn.commit()
conn.close()

print("Database initialized with schema and test user.")
