# 🔐 Flask OTP Signup App (Deployed on AWS EC2)

This is a secure **signup and email OTP verification** web application built using **Flask**, **MySQL**, and deployed on **AWS EC2** with **Gunicorn**, **Nginx**.

Users sign up with their email address, receive a One-Time Password (OTP), and verify it before completing registration.

### 🌐 Live Demo

Visit the live project here:

👉 [http://13.61.155.20](http://13.61.155.20)

> ✅ HTTPS will be available if a domain is mapped and SSL is active.

---

## 🚀 Features

- 🔐 User signup with email verification  
- 📩 OTP sent securely via Gmail SMTP  
- ✅ OTP verification to complete signup  
- 🛡️ Passwords stored securely with hashing  
- 🌍 Fully deployed on AWS EC2 using:  
  - Gunicorn + Nginx (production-ready)    
- 📦 Environment variables used to store secrets

---

## 🛠️ Tech Stack

| Frontend       | Backend      | Database | Deployment                 |
|----------------|--------------|----------|----------------------------|
| HTML, CSS, JS  | Python Flask | MySQL    | AWS EC2 + Gunicorn + Nginx |

---


## 🧠 How It Works

1. User enters email on the signup form  
2. Flask backend generates OTP  
3. OTP is sent via Gmail SMTP  
4. User enters OTP to verify identity  
5. Data is saved in MySQL database

---

## 🗂️ Project Structure

flask-otp-signup-aws/
│
├── Backend/
│   ├── app.py
│   ├── config.py
│   ├── otp_utils.py
│   └── db_setup.sql
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── requirements.txt
├── .gitignore
└── README.md

