from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models.user import db, User, Job
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config.from_object('config.Config')
db.init_app(app)

# Dummy data for testing
def create_test_data():
    with app.app_context():
        # Create test admin and user accounts
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            hashed_password = generate_password_hash("admin123", method='pbkdf2:sha256')
            admin = User(name='Admin User', email='admin@example.com', phone='1234567890', password=hashed_password, is_admin=True)
            db.session.add(admin)
        
        user = User.query.filter_by(email='user@example.com').first()
        if not user:
            hashed_password = generate_password_hash("user123", method='pbkdf2:sha256')
            user = User(name='Test User', email='user@example.com', phone='0987654321', password=hashed_password, is_admin=False)
            db.session.add(user)

        # Create some sample job opportunities
        if not Job.query.first():
            jobs = [
                Job(job_name="Software Engineer", company_name="TechCorp", location="New York", description="Develop software solutions."),
                Job(job_name="Data Analyst", company_name="DataTech", location="San Francisco", description="Analyze data trends."),
            ]
            db.session.bulk_save_objects(jobs)

        db.session.commit()

# Decorator to ensure the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login Route
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Validate user credentials from the database
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Found user: {user.name}, Role: {user.is_admin}")  # Debugging: Print user info
            print(f"Stored password hash: {user.password}")  # Debugging: Print stored hashed password

            if check_password_hash(user.password, password):
                print("Password is correct.")  # Debugging: Password check successful
                if (role == 'admin' and user.is_admin) or (role == 'user' and not user.is_admin):
                    session['user_id'] = user.id
                    session['username'] = user.name
                    session['role'] = role
                    print(f"Session set: {session['user_id']}, {session['role']}")  # Debugging: Print session data

                    return redirect(url_for('admin_dashboard') if role == 'admin' else url_for('user_dashboard'))
                else:
                    flash("Invalid role for the user.", "error")
            else:
                flash("Invalid password.", "error")
        else:
            flash("User not found.", "error")
    
    return render_template('login.html')


# Admin Dashboard Route
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        job_id = request.form.get('job_id')
        job_name = request.form['job_name']
        company_name = request.form['company_name']
        location = request.form['location']
        description = request.form['description']

        if job_id:
            job = Job.query.get(job_id)
            if job:
                job.job_name = job_name
                job.company_name = company_name
                job.location = location
                job.description = description
        else:
            new_job = Job(job_name=job_name, company_name=company_name, location=location, description=description)
            db.session.add(new_job)

        db.session.commit()
        flash("Job saved successfully.")

    jobs = Job.query.all()
    return render_template('admin_dashboard.html', jobs=jobs)

# Edit Job Route
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if session.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))

    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        job.job_name = request.form['job_name']
        job.company_name = request.form['company_name']
        job.location = request.form['location']
        job.description = request.form['description']
        db.session.commit()
        flash("Job updated successfully.")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_job.html', job=job)

# Delete Job Route
@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if session.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))

    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully.")
    return redirect(url_for('admin_dashboard'))

# User Dashboard Route
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('admin_dashboard'))

    jobs = Job.query.all()
    return render_template('user_dashboard.html', jobs=jobs)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Initialize and create tables on app startup
if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()
            create_test_data()
            print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

    app.run(debug=False, use_reloader=False)
