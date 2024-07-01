from flask import Flask, render_template, request, redirect, url_for, session  # Import necessary Flask modules
import mysql.connector  # Import MySQL connector module
from functools import wraps  # Import wraps function for decorators

app = Flask(__name__)  # Initialize Flask application

# Secret key for session management
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  # MySQL host
        user="root",  # MySQL username
        password="flora",  # MySQL password
        database="school"  # MySQL database name
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
                return "Access denied"  # Redirect to login or an error page if role not matched
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Get username from form
        password = request.form['password']  # Get password from form
        conn = get_db_connection()  # Connect to database
        cursor = conn.cursor(dictionary=True)  # Create cursor object
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))  # Execute SQL query
        user = cursor.fetchone()  # Fetch one row from the result
        conn.close()  # Close database connection
        if user:
            session['logged_in'] = True  # Set logged_in key in session to True
            session['user_id'] = user['id']  # Set user_id key in session to user's ID
            session['username'] = user['username']  # Set username key in session to user's username
            session['role'] = user['role']  # Set role key in session to user's role
            return redirect(url_for('dashboard'))  # Redirect to dashboard if login successful
        return "Invalid credentials"  # Return message for invalid credentials
    return render_template('login.html')  # Render login page if GET request


# Logout route
@app.route('/logout')
@login_required  # Ensure user is logged in to access this route
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('login'))  # Redirect to login page after logout


# Dashboard route
@app.route('/dashboard')
@login_required  # Ensure user is logged in to access this route
def dashboard():
    username = session.get('username')  # Get username from session
    role = session.get('role')  # Get role from session
    return render_template('dashboard.html', username=username, role=role)  # Render dashboard template


# Index route
@app.route('/')
@login_required  # Ensure user is logged in to access this route
def index():
    return render_template('login.html')  # Render login page


# Student Management routes

# Display students route
@app.route('/students')
@role_required('Admin', 'Teacher')  # Ensure user has Admin or Teacher role to access this route
@login_required  # Ensure user is logged in to access this route
def display_students():
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM students ORDER BY id DESC LIMIT 5')  # Execute SQL query
    students = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    return render_template('display_students.html', students=students)  # Render display_students template with students data

# Add student route
@app.route('/students/add')
@role_required('Admin')  # Ensure user has Admin role to access this route
@login_required  # Ensure user is logged in to access this route
def add_student():
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM classes')  # Execute SQL query to fetch classes
    classes = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    student = None  # Initialize student variable
    return render_template('add_student.html', classes=classes, student=student)  # Render add_student template with classes and student data


# Save student route
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
@app.route('/students/save', methods=['GET', 'POST'])
def save_student():
    if request.method == 'POST':  # Check if request method is POST
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        class_id = request.form['class_id']
        student_id = request.form.get('ID', '')  # Get student ID from form

        conn = get_db_connection()  # Connect to database
        cursor = conn.cursor(dictionary=True)  # Create cursor object

        if student_id == '':  # Check if student ID is empty (indicating a new student)
            query = 'INSERT INTO students (first_name, last_name, phone, email, address, class_id) VALUES (%s, %s, %s, %s, %s, %s)'  # SQL query to insert new student
            values = (first_name, last_name, phone, email, address, class_id)  # Values to insert into the query
        else:
            query = 'UPDATE students SET first_name = %s, last_name = %s, phone = %s, email = %s, address = %s, class_id = %s WHERE id = %s'  # SQL query to update existing student
            values = (first_name, last_name, phone, email, address, class_id, student_id)  # Values to update in the query

        cursor.execute(query, values)  # Execute SQL query with values
        conn.commit()  # Commit changes to database
        conn.close()  # Close database connection

        return redirect(url_for('display_students'))  # Redirect to display_students route after saving student


# Delete student route
@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def delete_student(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor()  # Create cursor object
    cursor.execute('DELETE FROM students WHERE id = %s', (id,))  # Execute SQL query to delete student with specified ID
    conn.commit()  # Commit changes to database
    cursor.close()  # Close cursor
    conn.close()  # Close database connection
    return redirect(url_for('display_students'))  # Redirect to display_students route after deleting student


# Edit student route
@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def edit_student(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM students WHERE id = %s', (id,))  # Execute SQL query to fetch student with specified ID
    student = cursor.fetchone()  # Fetch one row from the result
    cursor.execute('SELECT * FROM classes')  # Execute SQL query to fetch classes
    classes = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    return render_template('add_student.html', student=student, classes=classes)  # Render add_student template with student and classes data


# Teacher Management routes

# Display teachers route
@app.route('/teachers')
@role_required('Admin', 'Teacher')  # Ensure user has Admin or Teacher role to access this route
@login_required  # Ensure user is logged in to access this route
def display_teachers():
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM teachers ORDER BY id DESC LIMIT 5')  # Execute SQL query to fetch teachers
    teachers = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    return render_template('display_teachers.html', teachers=teachers)  # Render display_teachers template with teachers data

# Add teacher route
@app.route('/teachers/add')
@role_required('Admin')  # Ensure user has Admin role to access this route
@login_required  # Ensure user is logged in to access this route
def add_teacher():
    teacher = None  # Initialize teacher variable
    return render_template('add_teacher.html', teacher=teacher)  # Render add_teacher template with teacher data


# Save teacher route
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
@app.route('/teachers/save', methods=['GET', 'POST'])
def save_teacher():
    if request.method == 'POST':  # Check if request method is POST
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        teacher_id = request.form.get('ID', '')  # Get teacher ID from form

        conn = get_db_connection()  # Connect to database
        cursor = conn.cursor(dictionary=True)  # Create cursor object

        if teacher_id == '':  # Check if teacher ID is empty (indicating a new teacher)
            query = 'INSERT INTO teachers (first_name, last_name, phone, email, address) VALUES (%s, %s, %s, %s, %s)'  # SQL query to insert new teacher
            values = (first_name, last_name, phone, email, address)  # Values to insert into the query
        else:
            query = 'UPDATE teachers SET first_name = %s, last_name = %s, phone = %s, email = %s, address = %s WHERE id = %s'  # SQL query to update existing teacher
            values = (first_name, last_name, phone, email, address, teacher_id)  # Values to update in the query

        cursor.execute(query, values)  # Execute SQL query with values
        conn.commit()  # Commit changes to database
        conn.close()  # Close database connection

        return redirect(url_for('display_teachers'))  # Redirect to display_teachers route after saving teacher


# Delete teacher route
@app.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def delete_teacher(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor()  # Create cursor object
    cursor.execute('DELETE FROM teachers WHERE id = %s', (id,))  # Execute SQL query to delete teacher with specified ID
    conn.commit()  # Commit changes to database
    cursor.close()  # Close cursor
    conn.close()  # Close database connection
    return redirect(url_for('display_teachers'))  # Redirect to display_teachers route after deleting teacher


# Edit teacher route
@app.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def edit_teacher(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM teachers WHERE id = %s', (id,))  # Execute SQL query to fetch teacher with specified ID
    teacher = cursor.fetchone()  # Fetch one row from the result
    conn.close()  # Close database connection
    return render_template('add_teacher.html', teacher=teacher)  # Render add_teacher template with teacher data


# Subject Management routes

# Display subjects route
@app.route('/subjects')
@role_required('Admin', 'Teacher', 'Student')  # Ensure user has Admin, Teacher, or Student role to access this route
@login_required  # Ensure user is logged in to access this route
def display_subjects():
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM subjects')  # Execute SQL query to fetch subjects
    subjects = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    return render_template('display_subjects.html', subjects=subjects)  # Render display_subjects template with subjects data


# Add subject route
@app.route('/subjects/add')
@role_required('Admin')  # Ensure user has Admin role to access this route
@login_required  # Ensure user is logged in to access this route
def add_subject():
    conn = get_db_connection()  # Connect to database
    cursorclass = conn.cursor(dictionary=True)  # Create cursor object for classes
    cursorclass.execute('SELECT * FROM classes')  # Execute SQL query to fetch classes
    classes = cursorclass.fetchall()  # Fetch all rows from the result

    cursorteacher = conn.cursor(dictionary=True)  # Create cursor object for teachers
    cursorteacher.execute('SELECT * FROM teachers')  # Execute SQL query to fetch teachers
    Teachers = cursorteacher.fetchall()  # Fetch all rows from the result

    conn.close()  # Close database connection
    subject = None  # Initialize subject variable
    return render_template('add_subject.html', subject=subject, Teachers=Teachers, classes=classes)  # Render add_subject template with subject, Teachers, and classes data


# Save subject route
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
@app.route('/subjects/save', methods=['GET', 'POST'])
def save_subject():
    if request.method == 'POST':  # Check if request method is POST
        # Get form data
        name = request.form['name']
        class_id = request.form['class_id']
        Teacher_id = request.form['Teacher_id']
        subject_id = request.form.get('ID', '')  # Get subject ID from form

        conn = get_db_connection()  # Connect to database
        cursor = conn.cursor(dictionary=True)  # Create cursor object

        if subject_id == '':  # Check if subject ID is empty (indicating a new subject)
            query = 'INSERT INTO subjects (name, class_id, Teacher_id) VALUES (%s, %s, %s)'  # SQL query to insert new subject
            values = (name, class_id, Teacher_id)  # Values to insert into the query
        else:
            query = 'UPDATE subjects SET name = %s, class_id = %s, Teacher_id = %s WHERE id = %s'  # SQL query to update existing subject
            values = (name, class_id, Teacher_id, subject_id)  # Values to update in the query

        cursor.execute(query, values)  # Execute SQL query with values
        conn.commit()  # Commit changes to database
        conn.close()  # Close database connection

        return redirect(url_for('display_subjects'))  # Redirect to display_subjects route after saving subject


# Delete subject route
@app.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def delete_subject(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor()  # Create cursor object
    cursor.execute('DELETE FROM subjects WHERE id = %s', (id,))  # Execute SQL query to delete subject with specified ID
    conn.commit()  # Commit changes to database
    cursor.close()  # Close cursor
    conn.close()  # Close database connection
    return redirect(url_for('display_subjects'))  # Redirect to display_subjects route after deleting subject


# Edit subject route
@app.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def edit_subject(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM subjects WHERE id = %s', (id,))  # Execute SQL query to fetch subject with specified ID
    subject = cursor.fetchone()  # Fetch one row from the result

    cursorclass = conn.cursor(dictionary=True)  # Create cursor object for classes
    cursorclass.execute('SELECT * FROM classes')  # Execute SQL query to fetch classes
    classes = cursorclass.fetchall()  # Fetch all rows from the result

    cursorteacher = conn.cursor(dictionary=True)  # Create cursor object for teachers
    cursorteacher.execute('SELECT * FROM teachers')  # Execute SQL query to fetch teachers
    Teachers = cursorteacher.fetchall()  # Fetch all rows from the result

    conn.close()  # Close database connection
    return render_template('add_subject.html', subject=subject, classes=classes, Teachers=Teachers)  # Render add_subject template with subject, classes, and Teachers data


# Class Management routes

# Display classes route
@app.route('/classes')
@role_required('Admin', 'Teacher', 'Student')  # Ensure user has Admin, Teacher, or Student role to access this route
@login_required  # Ensure user is logged in to access this route
def display_classes():
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM classes')  # Execute SQL query to fetch classes
    classes = cursor.fetchall()  # Fetch all rows from the result
    conn.close()  # Close database connection
    return render_template('display_classes.html', classes=classes)  # Render display_classes template with classes data


# Add class route
@app.route('/classes/add')
@role_required('Admin')  # Ensure user has Admin role to access this route
@login_required  # Ensure user is logged in to access this route
def add_class():
    class_ = None  # Initialize class_ variable
    return render_template('add_class.html', class_=class_)  # Render add_class template with class_ data


# Save class route
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
@app.route('/classes/save', methods=['GET', 'POST'])
def save_class():
    if request.method == 'POST':  # Check if request method is POST
        # Get form data
        name = request.form['name']
        class_id = request.form.get('ID', '')  # Get class ID from form

        conn = get_db_connection()  # Connect to database
        cursor = conn.cursor(dictionary=True)  # Create cursor object

        if class_id == '':  # Check if class ID is empty (indicating a new class)
            query = 'INSERT INTO classes (name) VALUES (%s)'  # SQL query to insert new class
            values = (name,)  # Values to insert into the query
        else:
            query = 'UPDATE classes SET name = %s WHERE id = %s'  # SQL query to update existing class
            values = (name, class_id)  # Values to update in the query

        cursor.execute(query, values)  # Execute SQL query with values
        conn.commit()  # Commit changes to database
        conn.close()  # Close database connection

        return redirect(url_for('display_classes'))  # Redirect to display_classes route after saving class


# Delete class route
@app.route('/classes/delete/<int:id>', methods=['POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def delete_class(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor()  # Create cursor object
    cursor.execute('DELETE FROM classes WHERE id = %s', (id,))  # Execute SQL query to delete class with specified ID
    conn.commit()  # Commit changes to database
    cursor.close()  # Close cursor
    conn.close()  # Close database connection
    return redirect(url_for('display_classes'))  # Redirect to display_classes route after deleting class


# Edit class route
@app.route('/classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required  # Ensure user is logged in to access this route
@role_required('Admin')  # Ensure user has Admin role to access this route
def edit_class(id):
    conn = get_db_connection()  # Connect to database
    cursor = conn.cursor(dictionary=True)  # Create cursor object
    cursor.execute('SELECT * FROM classes WHERE id = %s', (id,))  # Execute SQL query to fetch class with specified ID
    class_ = cursor.fetchone()  # Fetch one row from the result
    conn.close()  # Close database connection
    return render_template('add_class.html', class_=class_)  # Render add_class template with class_ data


# Error handling for 404 Page Not Found error
@app.errorhandler(404)
def page_not_found(error):
    return "Page not found", 404  # Return custom 404 error page


# Main function to run the application
if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode

