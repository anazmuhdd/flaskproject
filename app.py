from flask import Flask, render_template, redirect, url_for, request, session, flash
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'png'}  # Add more file types if needed
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy user data for login validation (username: password, role)
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user': {'password': 'user123', 'role': 'user'}
}

# Store user profile data
user_profiles = {}

# Decorator to ensure the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Profile Data Input Route
@app.route('/profile_input', methods=['GET', 'POST'])
@login_required
def profile_input():
    username = session.get('username')
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        phone = request.form.get('phone')

        # Save profile data in a dictionary (mock database)
        user_profiles[username] = {
            'name': name,
            'email': email,
            'age': age,
            'phone': phone
        }
        flash("Profile information saved successfully!", "success")
        return redirect(url_for('profile_display'))
    
    return render_template('profile_input.html')

# Profile Display Route
@app.route('/profile_display', methods=['GET'])
@login_required
def profile_display():
    username = session.get('username')
    user_data = user_profiles.get(username, {})
    
    if not user_data:
        flash("No profile data found. Please fill in your profile information first.", "info")
        return redirect(url_for('profile_input'))

    return render_template('profile_display.html', user=user_data)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if the user exists and password is correct
        if username in users and users[username]['password'] == password and users[username]['role'] == role:
            session['username'] = username  # Save the username in session
            session['role'] = role  # Save the role of the user
            return redirect(url_for('user_dashboard') if role == 'user' else url_for('admin_dashboard'))
        else:
            flash("Invalid username, password, or role.", "error")
    
    return render_template('login.html')

# Admin Dashboard Route
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))  # Redirect if the user is not admin
    return render_template('admin_dashboard.html')

# User Dashboard Route
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('admin_dashboard'))  # Redirect if the user is not user
    return render_template('user_dashboard.html')

# Resume & Certifications Route
@app.route('/resume_certifications', methods=['GET', 'POST'])
@login_required
def resume_certifications():
    if session.get('role') != 'user':
        return redirect(url_for('admin_dashboard'))  # Redirect if the user is not a user

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part', 'error')
            return render_template('resume_certifications.html')

        resume = request.files['resume']
        certification = request.files['certification']

        if resume.filename == '':
            flash('No selected file for resume', 'error')
            return render_template('resume_certifications.html')

        if resume and allowed_file(resume.filename):
            resume_filename = secure_filename(resume.filename)
            resume.save(os.path.join(app.config['UPLOAD_FOLDER'], 'resume_' + session['username'] + '.' + resume_filename.rsplit('.', 1)[1].lower()))
            flash('Resume uploaded successfully!', 'success')
        else:
            flash('Invalid resume file type', 'error')
            return render_template('resume_certifications.html')

        if certification and certification.filename != '' and allowed_file(certification.filename):
            cert_filename = secure_filename(certification.filename)
            certification.save(os.path.join(app.config['UPLOAD_FOLDER'], 'certification_' + session['username'] + '.' + cert_filename.rsplit('.', 1)[1].lower()))
            flash('Certification uploaded successfully!', 'success')

        return redirect(url_for('user_dashboard'))

    return render_template('resume_certifications.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
