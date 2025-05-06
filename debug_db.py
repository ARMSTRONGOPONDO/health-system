# Create a script to check the database structure and users
import sqlite3
import os

def check_database():
    """
    Check if the database exists and print its structure
    """
    db_path = 'health_system.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    print(f"Database file found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  Row count: {count}")
            
            # If it's the user table, print users (without passwords)
            if table[0] == 'user':
                cursor.execute("SELECT id, username, is_admin FROM user")
                users = cursor.fetchall()
                print("  Users:")
                for user in users:
                    print(f"  - ID: {user[0]}, Username: {user[1]}, Admin: {user[2]}")
            
            print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_database()
