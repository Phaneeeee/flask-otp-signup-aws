# otp_utils.py

import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from .config import EMAIL_CONFIG

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp}")
    msg['Subject'] = "Your OTP Code"
    msg['From'] = EMAIL_CONFIG['EMAIL_ADDRESS']
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        smtp.send_message(msg)
