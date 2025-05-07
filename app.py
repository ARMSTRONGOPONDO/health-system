from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets
import logging

# Configuration
DATABASE = os.getenv('DATABASE_URL', 'health_system.db')
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(16))

app = Flask(__name__)
app.config.from_object(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# Logging Configuration
logging.basicConfig(level=logging.INFO)

# Database Setup
def initialize_database():
    """
    Initialize the SQLite database if it doesn't exist by applying the schema
    and creating default users.
    """
    if not os.path.exists(DATABASE):
        logging.info("Database not found. Initializing...")
        try:
            if not os.path.exists(SCHEMA_PATH):
                raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
            
            # Create database and apply schema
            with sqlite3.connect(DATABASE) as conn:
                with open(SCHEMA_PATH, 'r') as schema_file:
                    schema = schema_file.read()
                conn.executescript(schema)
                logging.info("Database initialized successfully!")
                
                # Add default users
                add_default_users(conn)
        except FileNotFoundError as fnf_error:
            logging.error(f"Error: {fnf_error}")
        except sqlite3.Error as db_error:
            logging.error(f"SQLite error: {db_error}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
        logging.info("Database already exists. Ensuring default users exist...")
        try:
            with sqlite3.connect(DATABASE) as conn:
                add_default_users(conn)

# Initialize the database
initialize_database()

def add_default_users(conn):
    """
    Add default testing users to the database if they do not already exist.
    """
    try:
        hashed_password = generate_password_hash("password", method="pbkdf2:sha256")
        
        # Insert default users only if they don't exist
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, is_admin, api_key) VALUES (?, ?, ?, ?)",
            ("Docter Testing", hashed_password, 0, "doctor_api_key")
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, is_admin, api_key) VALUES (?, ?, ?, ?)",
            ("Admin Testing", hashed_password, 1, "admin_api_key")
        )
        conn.commit()
        logging.info("Default users added successfully!")
    except sqlite3.Error as db_error:
        logging.error(f"Error adding default users: {db_error}")
        

def get_db():
    """Get a database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database schema."""
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA_PATH, mode='r') as f:
            db.executescript(f.read())

# CLI Commands
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    logging.info('Initialized the database.')

# Teardown Function
app.teardown_appcontext(close_db)

# Authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# API Authentication
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE api_key = ?', (api_key,)).fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

def get_user_by_username(username):
    """
    Retrieve a user from the database by username. Makes the username case-insensitive.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    user = cursor.fetchone()
    
    if user:
        # Convert to dictionary for easier access
        user_dict = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'is_admin': user[3],
            'api_key': user[4]
        }
        return user_dict
    return None

# When generating password hashes, specify the method:
def generate_password():
    # Use pbkdf2:sha256 instead of scrypt
    return generate_password_hash(password, method='pbkdf2:sha256')

# Update your login function to handle potential hash method issues
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Use get_user_by_username function
        user = get_user_by_username(username)
        
        if not user:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        
        try:
            # Try to check the password hash
            password_correct = check_password_hash(user['password'], password)
        except ValueError as e:
            # If there's an error with the hash format, log it and return an error
            app.logger.error(f"Password hash error: {str(e)}")
            flash('Authentication error. Please contact an administrator.', 'danger')
            return render_template('login.html')
            
        if not password_correct:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
            
        # Login successful
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    clients_count = db.execute('SELECT COUNT(*) as count FROM clients').fetchone()['count']
    programs_count = db.execute('SELECT COUNT(*) as count FROM programs').fetchone()['count']
    enrollments_count = db.execute('SELECT COUNT(*) as count FROM enrollments').fetchone()['count']
    
    return render_template('dashboard.html', 
                          clients_count=clients_count, 
                          programs_count=programs_count, 
                          enrollments_count=enrollments_count)

# Program Management
@app.route('/programs')
@login_required
def programs():
    db = get_db()
    programs = db.execute('SELECT * FROM programs').fetchall()
    return render_template('programs.html', programs=programs)

@app.route('/programs/add', methods=['GET', 'POST'])
@login_required
def add_program():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None
        
        if not name:
            error = 'Name is required.'
        
        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO programs (name, description) VALUES (?, ?)',
                (name, description)
            )
            db.commit()
            flash('Program added successfully!', 'success')
            return redirect(url_for('programs'))
        
        flash(error, 'error')
    
    return render_template('add_program.html')

@app.route('/programs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_program(id):
    db = get_db()
    program = db.execute('SELECT * FROM programs WHERE id = ?', (id,)).fetchone()
    
    if program is None:
        flash('Program not found', 'error')
        return redirect(url_for('programs'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        error = None
        
        if not name:
            error = 'Name is required.'
        
        if error is None:
            db.execute(
                'UPDATE programs SET name = ?, description = ? WHERE id = ?',
                (name, description, id)
            )
            db.commit()
            flash('Program updated successfully!', 'success')
            return redirect(url_for('programs'))
        
        flash(error, 'error')
    
    return render_template('edit_program.html', program=program)

# Client Management
@app.route('/clients')
@login_required
def clients():
    search = request.args.get('search', '')
    db = get_db()
    
    if search:
        clients = db.execute(
            'SELECT * FROM clients WHERE name LIKE ? OR id_number LIKE ?',
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        clients = db.execute('SELECT * FROM clients').fetchall()
    
    return render_template('clients.html', clients=clients, search=search)

@app.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        id_number = request.form['id_number']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form['address']
        error = None
        
        if not name:
            error = 'Name is required.'
        elif not id_number:
            error = 'ID Number is required.'
        
        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO clients (name, id_number, date_of_birth, gender, contact, address) VALUES (?, ?, ?, ?, ?, ?)',
                (name, id_number, date_of_birth, gender, contact, address)
            )
            db.commit()
            flash('Client added successfully!', 'success')
            return redirect(url_for('clients'))
        
        flash(error, 'error')
    
    return render_template('add_client.html')

@app.route('/clients/<int:id>')
@login_required
def view_client(id):
    db = get_db()
    client = db.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    
    if client is None:
        flash('Client not found', 'error')
        return redirect(url_for('clients'))
    
    enrollments = db.execute(
        'SELECT e.id, p.name, e.enrollment_date, e.status FROM enrollments e JOIN programs p ON e.program_id = p.id WHERE e.client_id = ?',
        (id,)
    ).fetchall()
    
    return render_template('view_client.html', client=client, enrollments=enrollments)

# Enrollment Management
@app.route('/clients/<int:id>/enroll', methods=['GET', 'POST'])
@login_required
def enroll_client(id):
    db = get_db()
    client = db.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    
    if client is None:
        flash('Client not found', 'error')
        return redirect(url_for('clients'))
    
    if request.method == 'POST':
        program_id = request.form['program_id']
        enrollment_date = request.form['enrollment_date']
        status = 'Active'
        error = None
        
        if not program_id:
            error = 'Program is required.'
        elif not enrollment_date:
            error = 'Enrollment date is required.'
        
        # Check if client is already enrolled in this program
        existing = db.execute(
            'SELECT * FROM enrollments WHERE client_id = ? AND program_id = ? AND status = "Active"',
            (id, program_id)
        ).fetchone()
        
        if existing:
            error = 'Client is already enrolled in this program.'
        
        if error is None:
            db.execute(
                'INSERT INTO enrollments (client_id, program_id, enrollment_date, status) VALUES (?, ?, ?, ?)',
                (id, program_id, enrollment_date, status)
            )
            db.commit()
            flash('Client enrolled successfully!', 'success')
            return redirect(url_for('view_client', id=id))
        
        flash(error, 'error')
    
    programs = db.execute('SELECT * FROM programs').fetchall()
    return render_template('enroll_client.html', client=client, programs=programs)

@app.route('/enrollments/<int:id>/update', methods=['POST'])
@login_required
def update_enrollment(id):
    status = request.form['status']
    
    db = get_db()
    enrollment = db.execute('SELECT * FROM enrollments WHERE id = ?', (id,)).fetchone()
    
    if enrollment is None:
        flash('Enrollment not found', 'error')
        return redirect(url_for('clients'))
    
    db.execute(
        'UPDATE enrollments SET status = ? WHERE id = ?',
        (status, id)
    )
    db.commit()
    
    flash('Enrollment updated successfully!', 'success')
    return redirect(url_for('view_client', id=enrollment['client_id']))

# API Endpoints
@app.route('/api/clients', methods=['GET'])
@api_key_required
def api_clients():
    db = get_db()
    clients = db.execute('SELECT * FROM clients').fetchall()
    
    result = []
    for client in clients:
        result.append({
            'id': client['id'],
            'name': client['name'],
            'id_number': client['id_number'],
            'date_of_birth': client['date_of_birth'],
            'gender': client['gender'],
            'contact': client['contact'],
            'address': client['address']
        })
    
    return jsonify(result)

@app.route('/api/clients/<int:id>', methods=['GET'])
@api_key_required
def api_client(id):
    db = get_db()
    client = db.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    
    if client is None:
        return jsonify({'error': 'Client not found'}), 404
    
    enrollments = db.execute(
        'SELECT e.id, p.name as program_name, e.enrollment_date, e.status FROM enrollments e JOIN programs p ON e.program_id = p.id WHERE e.client_id = ?',
        (id,)
    ).fetchall()
    
    enrollment_list = []
    for enrollment in enrollments:
        enrollment_list.append({
            'id': enrollment['id'],
            'program_name': enrollment['program_name'],
            'enrollment_date': enrollment['enrollment_date'],
            'status': enrollment['status']
        })
    
    result = {
        'id': client['id'],
        'name': client['name'],
        'id_number': client['id_number'],
        'date_of_birth': client['date_of_birth'],
        'gender': client['gender'],
        'contact': client['contact'],
        'address': client['address'],
        'enrollments': enrollment_list
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
