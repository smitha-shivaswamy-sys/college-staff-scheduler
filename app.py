from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'college_staff_secret_key_2025'

# Database initialization
DATABASE = 'college_staff.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db()
        cursor = conn.cursor()
        
        # Admins table
        cursor.execute('''
            CREATE TABLE admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Staff table
        cursor.execute('''
            CREATE TABLE staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                department TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Timetable table
        cursor.execute('''
            CREATE TABLE timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                class_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(staff_id) REFERENCES staff(id)
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(staff_id) REFERENCES staff(id)
            )
        ''')
        
        # Login logs table
        cursor.execute('''
            CREATE TABLE login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER,
                admin_id INTEGER,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                session_type TEXT
            )
        ''')
        
        # Leave requests table
        cursor.execute('''
            CREATE TABLE leave_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                leave_date TEXT NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(staff_id) REFERENCES staff(id)
            )
        ''')
        
        # Reassignment history table
        cursor.execute('''
            CREATE TABLE reassignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_staff_id INTEGER NOT NULL,
                new_staff_id INTEGER NOT NULL,
                timetable_id INTEGER NOT NULL,
                leave_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(original_staff_id) REFERENCES staff(id),
                FOREIGN KEY(new_staff_id) REFERENCES staff(id),
                FOREIGN KEY(timetable_id) REFERENCES timetable(id)
            )
        ''')
        
        # Create default admin
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO admins (username, password, email)
            VALUES (?, ?, ?)
        ''', ('admin', admin_password, 'admin@college.edu'))
        
        conn.commit()
        conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'user_type' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'staff':
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated_function

# Auto-rescheduling logic
def find_and_reassign_staff(leave_date, original_staff_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get original staff's schedule for that day
    cursor.execute('''
        SELECT * FROM timetable 
        WHERE staff_id = ? AND day = ?
    ''', (original_staff_id, leave_date))
    
    schedules = cursor.fetchall()
    
    for schedule in schedules:
        start_time = schedule['start_time']
        end_time = schedule['end_time']
        
        # Find available staff (not on leave, not already scheduled)
        cursor.execute('''
            SELECT s.id, s.name FROM staff s
            WHERE s.id != ? AND s.is_active = 1
            AND s.id NOT IN (
                SELECT staff_id FROM leave_requests 
                WHERE leave_date = ? AND status = 'approved'
            )
            AND s.id NOT IN (
                SELECT staff_id FROM timetable 
                WHERE day = ? 
                AND ((start_time <= ? AND end_time > ?) 
                     OR (start_time < ? AND end_time >= ?)
                     OR (start_time >= ? AND end_time <= ?))
            )
            LIMIT 1
        ''', (original_staff_id, leave_date, leave_date, start_time, start_time, 
              end_time, end_time, start_time, end_time))
        
        alternative_staff = cursor.fetchone()
        
        if alternative_staff:
            new_staff_id = alternative_staff['id']
            
            # Create reassignment record
            cursor.execute('''
                INSERT INTO reassignments 
                (original_staff_id, new_staff_id, timetable_id, leave_date)
                VALUES (?, ?, ?, ?)
            ''', (original_staff_id, new_staff_id, schedule['id'], leave_date))
            
            # Update timetable with new staff
            cursor.execute('''
                UPDATE timetable 
                SET staff_id = ? 
                WHERE id = ?
            ''', (new_staff_id, schedule['id']))
    
    conn.commit()
    conn.close()

# ==================== ADMIN ROUTES ====================

@app.route('/')
def index():
    if 'user_type' in session:
        if session['user_type'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('staff_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password'], password):
            session['user_id'] = admin['id']
            session['user_type'] = 'admin'
            session['username'] = admin['username']
            
            # Log admin login
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO login_logs (admin_id, session_type)
                VALUES (?, ?)
            ''', (admin['id'], 'admin'))
            conn.commit()
            conn.close()
            
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total FROM staff WHERE is_active = 1')
    total_staff = cursor.fetchone()['total']
    
    # Get logged-in staff count (check recent login logs)
    cursor.execute('''
        SELECT COUNT(DISTINCT staff_id) as logged_in FROM login_logs 
        WHERE session_type = 'staff' 
        AND login_time > datetime('now', '-24 hours')
        AND logout_time IS NULL
    ''')
    logged_in_staff = cursor.fetchone()['logged_in']
    
    # Get recent logins
    cursor.execute('''
        SELECT s.name, l.login_time FROM login_logs l
        JOIN staff s ON l.staff_id = s.id
        WHERE session_type = 'staff'
        ORDER BY l.login_time DESC LIMIT 10
    ''')
    recent_logins = cursor.fetchall()
    
    # Get pending leave requests
    cursor.execute('''
        SELECT l.*, s.name FROM leave_requests l
        JOIN staff s ON l.staff_id = s.id
        WHERE l.status = 'pending'
        ORDER BY l.created_at DESC
    ''')
    pending_leaves = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         total_staff=total_staff,
                         logged_in_staff=logged_in_staff,
                         recent_logins=recent_logins,
                         pending_leaves=pending_leaves)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@admin_required
def add_staff():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')
        phone = request.form.get('phone')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO staff (name, email, password, department, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, department, phone))
            
            conn.commit()
            conn.close()
            
            return render_template('add_staff.html', success='Staff member added successfully!')
        except sqlite3.IntegrityError:
            return render_template('add_staff.html', error='Email already exists')
    
    return render_template('add_staff.html')

@app.route('/admin/staff/view')
@admin_required
def view_staff():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM staff WHERE is_active = 1 ORDER BY name')
    staff_list = cursor.fetchall()
    conn.close()
    
    return render_template('view_staff.html', staff=staff_list)

@app.route('/admin/staff/delete/<int:staff_id>', methods=['POST'])
@admin_required
def delete_staff(staff_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Soft delete - mark staff as inactive instead of deleting
    # This preserves historical data in timetable, attendance, and leave records
    cursor.execute('UPDATE staff SET is_active = 0 WHERE id = ?', (staff_id,))
    
    # Remove future timetable entries for this staff member
    cursor.execute('DELETE FROM timetable WHERE staff_id = ?', (staff_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_staff'))

@app.route('/admin/timetable/create', methods=['GET', 'POST'])
@admin_required
def create_timetable():
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')
        class_name = request.form.get('class_name')
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO timetable (staff_id, day, start_time, end_time, location, class_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (staff_id, day, start_time, end_time, location, class_name))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_timetable'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM staff WHERE is_active = 1')
    staff_list = cursor.fetchall()
    conn.close()
    
    return render_template('create_timetable.html', staff=staff_list)

@app.route('/admin/timetable/view')
@admin_required
def view_timetable():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, s.name FROM timetable t
        JOIN staff s ON t.staff_id = s.id
        ORDER BY t.day, t.start_time
    ''')
    timetable = cursor.fetchall()
    conn.close()
    
    return render_template('view_timetable.html', timetable=timetable)

@app.route('/admin/timetable/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_timetable(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')
        class_name = request.form.get('class_name')
        
        cursor.execute('''
            UPDATE timetable 
            SET day = ?, start_time = ?, end_time = ?, location = ?, class_name = ?
            WHERE id = ?
        ''', (day, start_time, end_time, location, class_name, id))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_timetable'))
    
    cursor.execute('SELECT * FROM timetable WHERE id = ?', (id,))
    entry = cursor.fetchone()
    conn.close()
    
    return render_template('edit_timetable.html', entry=entry)

@app.route('/admin/leaves/view')
@admin_required
def view_leaves():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*, s.name FROM leave_requests l
        JOIN staff s ON l.staff_id = s.id
        ORDER BY l.created_at DESC
    ''')
    leaves = cursor.fetchall()
    conn.close()
    
    return render_template('view_leaves.html', leaves=leaves)

@app.route('/admin/leave/approve/<int:id>', methods=['POST'])
@admin_required
def approve_leave(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leave_requests WHERE id = ?', (id,))
    leave = cursor.fetchone()
    
    if leave:
        cursor.execute('UPDATE leave_requests SET status = ? WHERE id = ?', ('approved', id))
        conn.commit()
        
        # Auto-reassign staff
        find_and_reassign_staff(leave['leave_date'], leave['staff_id'])
    
    conn.close()
    return redirect(url_for('view_leaves'))

@app.route('/admin/leave/reject/<int:id>', methods=['POST'])
@admin_required
def reject_leave(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE leave_requests SET status = ? WHERE id = ?', ('rejected', id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_leaves'))

@app.route('/admin/logins/view')
@admin_required
def view_logins():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT l.*, s.name FROM login_logs l
        LEFT JOIN staff s ON l.staff_id = s.id
        ORDER BY l.login_time DESC LIMIT 100
    ''')
    logins = cursor.fetchall()
    conn.close()
    
    return render_template('view_logins.html', logins=logins)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ==================== STAFF ROUTES ====================

@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staff WHERE email = ?', (email,))
        staff = cursor.fetchone()
        conn.close()
        
        if staff and check_password_hash(staff['password'], password):
            session['user_id'] = staff['id']
            session['user_type'] = 'staff'
            session['username'] = staff['name']
            
            # Log staff login
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO login_logs (staff_id, session_type)
                VALUES (?, ?)
            ''', (staff['id'], 'staff'))
            conn.commit()
            conn.close()
            
            return redirect(url_for('staff_dashboard'))
        else:
            return render_template('staff_login.html', error='Invalid credentials')
    
    return render_template('staff_login.html')

@app.route('/staff/dashboard')
@staff_required
def staff_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    staff_id = session['user_id']
    
    # Get staff details
    cursor.execute('SELECT * FROM staff WHERE id = ?', (staff_id,))
    staff = cursor.fetchone()
    
    # Get today's schedule
    cursor.execute('''
        SELECT * FROM timetable 
        WHERE staff_id = ? 
        ORDER BY start_time
    ''', (staff_id,))
    schedule = cursor.fetchall()
    
    conn.close()
    
    return render_template('staff_dashboard.html', staff=staff, schedule=schedule)

@app.route('/staff/attendance/mark', methods=['GET', 'POST'])
@staff_required
def mark_attendance():
    if request.method == 'POST':
        date = request.form.get('date')
        status = request.form.get('status')
        reason = request.form.get('reason')
        
        if status == 'leave':
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO leave_requests (staff_id, leave_date, reason, status)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], date, reason, 'pending'))
            
            conn.commit()
            conn.close()
            
            return render_template('mark_attendance.html', success='Leave request submitted!')
        else:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO attendance (staff_id, date, status, reason)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], date, status, reason))
            
            conn.commit()
            conn.close()
            
            return render_template('mark_attendance.html', success='Attendance marked!')
    
    return render_template('mark_attendance.html')

@app.route('/staff/schedule')
@staff_required
def view_schedule():
    conn = get_db()
    cursor = conn.cursor()
    
    staff_id = session['user_id']
    
    cursor.execute('''
        SELECT t.*, 
            CASE WHEN r.id IS NOT NULL THEN 'Reassigned' ELSE 'Original' END as assignment_type
        FROM timetable t
        LEFT JOIN reassignments r ON t.id = r.timetable_id
        WHERE t.staff_id = ?
        ORDER BY t.day, t.start_time
    ''', (staff_id,))
    
    schedule = cursor.fetchall()
    conn.close()
    
    return render_template('view_schedule.html', schedule=schedule)

@app.route('/staff/logout')
def staff_logout():
    session.clear()
    return redirect(url_for('staff_login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
