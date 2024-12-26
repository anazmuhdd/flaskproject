class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:admin@localhost/flaskproject'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Enable SQL query logging for debugging
    SECRET_KEY = 'your_secure_secret_key_here'  # Replace with a secure key
