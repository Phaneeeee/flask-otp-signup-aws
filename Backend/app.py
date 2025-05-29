import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import mysql.connector
import bcrypt
from config import Config
from otp_utils import generate_otp, send_otp_email

# Initialize Flask app
app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
app.config.from_object(Config)

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Serve frontend pages
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/otp')
def otp_page():
    return render_template('otp.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        print("Signup request data:", data, flush=True)

        email = data.get('email')
        name = data.get('full_name') or data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            return jsonify({'error': 'Email, name, and password are required'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=10)

        try:
            send_otp_email(email, otp)
        except Exception as e:
            print("Error sending OTP:", e, flush=True)
            return jsonify({'error': 'Failed to send OTP email'}), 500

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, otp_code, otp_expiry, is_verified)
                VALUES (%s, %s, %s, %s, %s, FALSE)
                ON DUPLICATE KEY UPDATE
                    otp_code = VALUES(otp_code),
                    otp_expiry = VALUES(otp_expiry),
                    is_verified = FALSE
            """, (name, email, hashed_password, otp, otp_expiry))
            conn.commit()
        except Exception as e:
            print("Database error during signup:", e, flush=True)
            return jsonify({'error': 'Database error: ' + str(e)}), 500
        finally:
            cursor.close()
            conn.close()

        return jsonify({'message': 'OTP sent to your email'}), 200

    except Exception as e:
        print("Signup route error:", e, flush=True)
        return jsonify({'error': 'Signup failed due to server error'}), 500

# OTP verification
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data['email']
    otp = data['otp']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT otp_code, otp_expiry FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if str(user['otp_code']) != str(otp):
            return jsonify({'error': 'Invalid OTP'}), 400

        otp_expiry = user['otp_expiry']
        if isinstance(otp_expiry, str):
            otp_expiry = datetime.strptime(otp_expiry, '%Y-%m-%d %H:%M:%S')

        if datetime.now() > otp_expiry:
            return jsonify({'error': 'OTP expired'}), 400

        cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = %s", (email,))
        conn.commit()
        return jsonify({'message': 'OTP verified successfully!'}), 200

    except Exception as e:
        print("Error verifying OTP:", e)
        return jsonify({'error': 'Something went wrong'}), 500

    finally:
        cursor.close()
        conn.close()

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    raw_password = data.get('password')

    if not email or not raw_password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password_hash, is_verified FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user['is_verified']:
            return jsonify({'error': 'Email not verified'}), 401

        stored_hash = user['password_hash']
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')

        if bcrypt.checkpw(raw_password.encode('utf-8'), stored_hash):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid password'}), 401

    except Exception as e:
        print("Login error:", e)
        return jsonify({'error': 'Something went wrong'}), 500

    finally:
        cursor.close()
        conn.close()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
