from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, render_template
import mysql.connector
import bcrypt
import os
from .config import DB_CONFIG
from .otp_utils import generate_otp, send_otp_email
from datetime import datetime, timedelta

conn = mysql.connector.connect(**DB_CONFIG)

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

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

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        print("Signup request data:", data, flush=True)

        email = data.get('email')
        name = data.get('full_name') or data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            print("Missing required signup fields", flush=True)
            return jsonify({'error': 'Email, name, and password are required'}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')

        # Generate OTP and expiry time
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=10)

        try:
            send_otp_email(email, otp)
            print(f"OTP sent to email: {email}", flush=True)
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
            """, (name, email, hashed_password_str, otp, otp_expiry))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"User {email} signed up successfully with OTP generated.", flush=True)

        except Exception as e:
            print("Database error during signup:", e, flush=True)
            return jsonify({'error': 'Database error: ' + str(e)}), 500

        return jsonify({'message': 'OTP sent to your email'}), 200

    except Exception as e:
        print("Signup route error:", e, flush=True)
        return jsonify({'error': 'Signup failed due to server error'}), 500


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

        print("Received OTP:", otp)
        print("Stored OTP:", user['otp_code'])
        print("OTP expiry:", user['otp_expiry'])

        if str(user['otp_code']) != str(otp):
            return jsonify({'error': 'Invalid OTP'}), 400

        otp_expiry = user['otp_expiry']
        if isinstance(otp_expiry, str):
            otp_expiry = datetime.strptime(otp_expiry, '%Y-%m-%d %H:%M:%S')  # Adjust format

        if datetime.now() > otp_expiry:
            return jsonify({'error': 'OTP expired'}), 400

        cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = %s", (email,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'OTP verified successfully!'}), 200

    except Exception as e:
        print("Error verifying OTP:", e)
        return jsonify({'error': 'Something went wrong'}), 500


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

        # stored_hash from DB is string, convert to bytes for bcrypt
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
        if cursor: cursor.close()
        if conn: conn.close()

        
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
            
