from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import text

# Initialize the Flask app
app = Flask(__name__)

# Set the connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:admin@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Test the connection
try:
    # Try to connect and perform a simple query (wrapped in text())
    with app.app_context():
        result = db.session.execute(text("SELECT 1"))
        print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")
