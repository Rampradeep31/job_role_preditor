import sqlite3
import os

# 1. Connect to the database
# Adjust 'database/users.db' if your path is different (e.g., 'backend/database/users.db')
db_path = os.path.join("database", "users.db")

print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. TYPE THE EXACT USERNAME HERE 👇
    username_to_promote = "admin123"  # Change this to the username you want to promote
    
    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username_to_promote,))
    user = cursor.fetchone()

    if user:
        print(f"Found user: {user[1]} (ID: {user[0]})")
        
        # 3. Update the role to 'admin'
        cursor.execute("UPDATE users SET role='admin' WHERE username=?", (username_to_promote,))
        conn.commit()
        print(f"✅ SUCCESS! User '{username_to_promote}' is now an Admin.")
    else:
        print(f"❌ ERROR: User '{username_to_promote}' not found. Please check spelling.")

    conn.close()

except Exception as e:
    print("❌ ERROR:", e)