# Create a script to reset or create an admin user with the correct hash method
import sqlite3
from werkzeug.security import generate_password_hash

def create_admin_user(username, password):
    # Connect to the database
    conn = sqlite3.connect('health_system.db')
    cursor = conn.cursor()
    
    # Check if the user already exists
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    # Generate password hash using pbkdf2
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    if user:
        # Update existing user
        cursor.execute(
            "UPDATE user SET password = ? WHERE username = ?",
            (password_hash, username)
        )
        print(f"Updated password for user: {username}")
    else:
        # Create new admin user
        cursor.execute(
            "INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)",
            (username, password_hash, 1)
        )
        print(f"Created new admin user: {username}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    create_admin_user(username, password)
    print("Admin user created/updated successfully!")
