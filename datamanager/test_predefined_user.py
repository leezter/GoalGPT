import sqlite3

# Path to your SQLite database file
DB_PATH = "database.db"

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Query for the predefined test user
cur.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", ("test@example.com",))
user = cur.fetchone()

if user:
    print(f"Test user found: id={user[0]}, name={user[1]}, email={user[2]}, password_hash={user[3]}")
else:
    print("Test user not found.")

conn.close()
