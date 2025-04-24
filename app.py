from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import secrets

# Configuration
DATABASE = 'health_system.db'
SECRET_KEY = secrets.token_hex(16)

app = Flask(__name__)
app.config.from_object(__name__)

# Database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())  

@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    print('Initialized the database.')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        
        flash(error, 'error')
    
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
