from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Admin, Student, Subject, Marks
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return "A+"
    elif percentage >= 75:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    else:
        return "Fail"

def is_admin_logged_in():
    """Check if admin is logged in"""
    return 'admin_id' in session

def init_db():
    """Initialize database tables and default admin"""
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

# Student Routes
@app.route('/')
def index():
    """Homepage - Student search page"""
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    """Show student result"""
    roll_no = request.form.get('roll_no', '').strip()
    
    if not roll_no:
        flash('Please enter a roll number', 'error')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(roll_no=roll_no).first()
    
    if not student:
        return render_template('result.html', student=None, error='Result not found.')
    
    # Get all marks for this student
    marks_list = Marks.query.filter_by(student_id=student.id).all()
    
    if not marks_list:
        return render_template('result.html', student=student, marks_list=[], 
                             total=0, percentage=0, grade='N/A', error='No marks found for this student.')
    
    # Calculate total, percentage, and grade
    total_marks = sum(m.marks for m in marks_list)
    num_subjects = len(marks_list)
    percentage = (total_marks / (num_subjects * 100)) * 100
    grade = calculate_grade(percentage)
    
    return render_template('result.html', student=student, marks_list=marks_list,
                         total=total_marks, percentage=round(percentage, 2), grade=grade)

# Admin Routes
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """Admin registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not password or not confirm_password:
            flash('Please fill all fields', 'error')
            return render_template('admin_register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'error')
            return render_template('admin_register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('admin_register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('admin_register.html')
        
        # Check if username already exists
        existing = Admin.query.filter_by(username=username).first()
        if existing:
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('admin_register.html')
        
        # Create new admin
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('admin_login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not is_admin_logged_in():
        flash('Please login to access the dashboard', 'error')
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    total_results = Marks.query.count()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         total_results=total_results)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    """Add new student"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        roll_no = request.form.get('roll_no', '').strip()
        name = request.form.get('name', '').strip()
        class_name = request.form.get('class_name', '').strip()
        
        if not roll_no or not name or not class_name:
            flash('Please fill all fields', 'error')
            return render_template('add_student.html')
        
        # Check if roll number already exists
        existing = Student.query.filter_by(roll_no=roll_no).first()
        if existing:
            flash('Roll number already exists', 'error')
            return render_template('add_student.html')
        
        student = Student(roll_no=roll_no, name=name, class_name=class_name)
        db.session.add(student)
        db.session.commit()
        
        flash('Student added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_student.html')

@app.route('/admin/add_subject', methods=['GET', 'POST'])
def add_subject():
    """Add new subject"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            flash('Please enter subject name', 'error')
            return render_template('add_subject.html')
        
        # Check if subject already exists
        existing = Subject.query.filter_by(name=name).first()
        if existing:
            flash('Subject already exists', 'error')
            return render_template('add_subject.html')
        
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_subject.html')

@app.route('/admin/add_marks', methods=['GET', 'POST'])
def add_marks():
    """Add marks for student"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    students = Student.query.all()
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        marks = request.form.get('marks', '').strip()
        
        if not student_id or not subject_id or not marks:
            flash('Please fill all fields', 'error')
            return render_template('add_marks.html', students=students, subjects=subjects)
        
        try:
            marks_int = int(marks)
            if marks_int < 0 or marks_int > 100:
                flash('Marks must be between 0 and 100', 'error')
                return render_template('add_marks.html', students=students, subjects=subjects)
        except ValueError:
            flash('Marks must be a valid number', 'error')
            return render_template('add_marks.html', students=students, subjects=subjects)
        
        # Check if marks already exist for this student-subject combination
        existing = Marks.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if existing:
            # Update existing marks
            existing.marks = marks_int
            db.session.commit()
            flash('Marks updated successfully!', 'success')
        else:
            # Create new marks entry
            marks_entry = Marks(student_id=student_id, subject_id=subject_id, marks=marks_int)
            db.session.add(marks_entry)
            db.session.commit()
            flash('Marks added successfully!', 'success')
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_marks.html', students=students, subjects=subjects)

@app.route('/admin/view_results')
def view_results():
    """View all results"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    students = Student.query.all()
    results = []
    
    for student in students:
        marks_list = Marks.query.filter_by(student_id=student.id).all()
        if marks_list:
            total_marks = sum(m.marks for m in marks_list)
            num_subjects = len(marks_list)
            percentage = (total_marks / (num_subjects * 100)) * 100
            grade = calculate_grade(percentage)
            results.append({
                'student': student,
                'total': total_marks,
                'percentage': round(percentage, 2),
                'grade': grade,
                'num_subjects': num_subjects
            })
        else:
            results.append({
                'student': student,
                'total': 0,
                'percentage': 0,
                'grade': 'N/A',
                'num_subjects': 0
            })
    
    return render_template('view_results.html', results=results)

@app.route('/admin/delete_student/<int:student_id>')
def delete_student(student_id):
    """Delete a student"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('view_results'))

@app.route('/admin/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    """Delete a subject"""
    if not is_admin_logged_in():
        flash('Please login to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# Initialize database on app startup
init_db()

if __name__ == '__main__':
    app.run(debug=True)

