from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector # Import MySQL connector module
import mariadb
from functools import wraps # Import wraps function for decorators

app = Flask(__name__) # Initialize Flask application


# Secret key for session management
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    conn = mariadb.connect(
        host="localhost", # MySQL host
        port=3305,
        user="root", # MySQL username
        password="flora",  # MySQL password
        database="school" # MySQL database name
    )
    return conn

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))  # Redirect to login page if not logged in
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if user has required role
def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                return "Access denied" # Redirect to login or an error page if role not matched
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # Get username from form
        password = request.form['password'] # Get password from form
        conn = get_db_connection()          # Connect to database
        cursor = conn.cursor(dictionary=True)   # Create cursor object
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()  # Fetch one row from the result
        conn.close() # Close database connection
        if user:
            session['logged_in'] = True # Set logged_in key in session to True
            session['user_id'] = user['id']  # Set user_id key in session to user's ID
            session['username'] = user['username'] # Set username key in session to user's username
            session['role'] = user['role'] # Set role key in session to user's role
            return redirect(url_for('dashboard')) # Redirect to dashboard if login successful
        return "Invalid credentials"  # Return message for invalid credentials
    return render_template('login.html') # Render login page if GET request

# Logout route
@app.route('/logout')
@login_required # Ensure user is logged in to access this route
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('login')) # Redirect to login page after logout


# Dashboard route
@app.route('/dashboard')
@login_required  # Ensure user is logged in to access this route
def dashboard():
    username = session.get('username')  # Get username from session
    role = session.get('role')  # Get role from session
    return render_template('dashboard.html', username=username, role=role) # Render dashboard template

# Index route
@app.route('/')
@login_required # Ensure user is logged in to access this route
def index():
    return render_template('login.html') # Render login page

# Student Management routes

# Display students route
@app.route('/students')
@role_required('admin', 'teacher') # Ensure user has Admin or Teacher role to access this route
@login_required   # Ensure user is logged in to access this route
def display_students():
    conn = get_db_connection() # Connect to database
    cursor = conn.cursor(dictionary=True) # Create cursor object
    cursor.execute('SELECT * FROM students ORDER BY id DESC')
    students = cursor.fetchall() # Fetch all rows from the result
    conn.close() # Close database connection
    return render_template('display_students.html', students=students)  # Render display_students template with students data

# Add student route
@app.route('/students/add')
@role_required('admin')
@login_required
def add_student():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM classes')
    classes = cursor.fetchall()
    conn.close()
    student = None
    return render_template('add_student.html', classes=classes, student=student)

# Save student route
@app.route('/students/save', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def save_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        class_id = request.form['class_id']
        student_id = request.form.get('id', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if student_id == '':
            query = 'INSERT INTO students (first_name, last_name, phone, email, address, class_id) VALUES (%s, %s, %s, %s, %s, %s)'
            values = (first_name, last_name, phone, email, address, class_id)
        else:
            query = 'UPDATE students SET first_name = %s, last_name = %s, phone = %s, email = %s, address = %s, class_id = %s WHERE id = %s'
            values = (first_name, last_name, phone, email, address, class_id, student_id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return redirect(url_for('display_students'))
    
# Delete student route
@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('display_students'))


# Edit student route
@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
    student = cursor.fetchone()
    cursor.execute('SELECT * FROM classes')
    classes = cursor.fetchall()
    conn.close()
    return render_template('add_student.html', student=student, classes=classes)

# Teacher Management routes

# Display teachers route
@app.route('/teachers')
@role_required('admin', 'teacher')
@login_required
def display_teachers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM teachers ORDER BY id DESC')
    teachers = cursor.fetchall()
    conn.close()
    return render_template('display_teachers.html', teachers=teachers)

# Add teacher route
@app.route('/teachers/add')
@role_required('admin')
@login_required
def add_teacher():
    teacher = None
    return render_template('add_teacher.html', teacher=teacher)

# Save teacher route
@app.route('/teachers/save', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def save_teacher():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        teacher_id = request.form.get('ID', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if teacher_id == '':
            query = 'INSERT INTO teachers (first_name, last_name, phone, email, address) VALUES (%s, %s, %s, %s, %s)'
            values = (first_name, last_name, phone, email, address)
        else:
            query = 'UPDATE teachers SET first_name = %s, last_name = %s, phone = %s, email = %s, address = %s WHERE id = %s'
            values = (first_name, last_name, phone, email, address, teacher_id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return redirect(url_for('display_teachers'))
    
# Delete teacher route
@app.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_teacher(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teachers WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('display_teachers'))

# Edit teacher route
@app.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_teacher(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM teachers WHERE id = %s', (id,))
    teacher = cursor.fetchone()
    conn.close()
    return render_template('add_teacher.html', teacher=teacher)

# Subject Management routes
# Display subjects route
@app.route('/subjects')
@role_required('admin', 'teacher', 'student')
@login_required
def display_subjects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM subjects ORDER BY id DESC')
    subjects = cursor.fetchall()
    conn.close()
    return render_template('display_subjects.html', subjects=subjects)

# Add subject route
@app.route('/subjects/add')
@role_required('admin')
@login_required
def add_subject():
    conn = get_db_connection()
    cursorclass = conn.cursor(dictionary=True)
    cursorclass.execute('SELECT * FROM classes')
    classes = cursorclass.fetchall()

    cursorteacher = conn.cursor(dictionary=True)
    cursorteacher.execute('SELECT * FROM teachers')
    teachers = cursorteacher.fetchall()

    conn.close()
    subject = None
    return render_template('add_subject.html', subject=subject, teachers=teachers, classes=classes)

# Save subject route
@app.route('/subjects/save', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def save_subject():
    if request.method == 'POST':
         # Get form data
        name = request.form['name']
        class_id = request.form['class_id']
        teacher_id = request.form['Teacher_id']
        subject_id = request.form.get('id', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if subject_id == '':
            query = 'INSERT INTO subjects (name, class_id, teacher_id) VALUES (%s, %s, %s)'
            values = (name, class_id, teacher_id)
        else:
            query = 'UPDATE subjects SET name = %s, class_id = %s, teacher_id = %s WHERE id = %s'
            values = (name, class_id, teacher_id, subject_id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return redirect(url_for('display_subjects'))

# Delete subject route
@app.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_subject(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subjects WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('display_subjects'))

# Edit subject route
@app.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_subject(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM subjects WHERE id = %s', (id,))
    subject = cursor.fetchone()

    cursorclass = conn.cursor(dictionary=True)
    cursorclass.execute('SELECT * FROM classes')
    classes = cursorclass.fetchall()

    cursorteacher = conn.cursor(dictionary=True)
    cursorteacher.execute('SELECT * FROM teachers')
    teachers = cursorteacher.fetchall()

    conn.close()
    return render_template('add_subject.html', subject=subject, classes=classes, teachers=teachers)

# Class Management routes

# Display classes route
@app.route('/classes')
@role_required('admin', 'teacher', 'student')
@login_required
def display_classes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM classes ORDER BY id DESC')
    classes = cursor.fetchall()
    conn.close()
    return render_template('display_classes.html', classes=classes)

# Add class route
@app.route('/classes/add', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def add_class():
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO classes (name, capacity) VALUES (%s, %s)',
                       (name, capacity))
        conn.commit()
        conn.close()
        return redirect(url_for('display_classes'))
    return render_template('add_class.html', class_=None)

# Save class route
@app.route('/classes/save', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def save_class():
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['Capacity']
        class_id = request.form.get('id', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if class_id == '':
            query = 'INSERT INTO classes (name, capacity) VALUES (%s, %s)'
            values = (name, capacity)
        else:
            query = 'UPDATE classes SET name = %s, capacity = %s WHERE id = %s'
            values = (name, capacity, class_id)

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return redirect(url_for('display_classes'))
    
# Delete class route
@app.route('/classes/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_class(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM classes WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('display_classes'))

# Edit class route
@app.route('/classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_class(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM classes WHERE id = %s', (id,))
    class_ = cursor.fetchone()
    conn.close()
    return render_template('add_class.html', class_=class_)

# Error handling for 404 Page Not Found error
@app.errorhandler(404)
def page_not_found(error):
    return "Page not found", 404

# Main function to run the application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
