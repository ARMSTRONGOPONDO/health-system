import sqlite3
from werkzeug.security import generate_password_hash
import secrets

# Connect to the database
conn = sqlite3.connect('health_system.db')
cursor = conn.cursor()

# Generate a new API key
api_key = secrets.token_hex(16)

# Create a new admin user with password 'admin123'
username = 'admin'
password = 'admin123'  # Simple password for testing
password_hash = generate_password_hash(password)

# First, check if the admin user already exists
cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
user = cursor.fetchone()

if user:
    # Update existing admin user
    cursor.execute(
        'UPDATE users SET password = ?, api_key = ? WHERE username = ?',
        (password_hash, api_key, username)
    )
    print(f"Admin user updated with new password: {password}")
else:
    # Create new admin user
    cursor.execute(
        'INSERT INTO users (username, password, api_key) VALUES (?, ?, ?)',
        (username, password_hash, api_key)
    )
    print(f"New admin user created with password: {password}")

# Commit changes and close connection
conn.commit()
conn.close()

print("Admin credentials:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"API Key: {api_key}")