# EcoReminder — Smart Dustbin Alert System# EcoReminder — Smart Dustbin Alert System







































































































- Add geolocation on reports and a map view.- Add pagination and search in dashboards.- Add email notifications when reports are created / updated.- Add user roles and permissions more robustly with `flask-login`.## 🔧 Optional Enhancements- If you want to create additional collector accounts, insert them into the `collectors` table manually or add a registration flow as needed.- Uploaded images are stored in `static/images/uploads/`.## 📌 Notes```│   ├── images/│   ├── js/│   ├── css/├── static/││   ├── admin_dashboard.html│   ├── collector_dashboard.html│   ├── citizen_dashboard.html│   ├── report.html│   ├── register.html│   ├── login.html│   ├── index.html│   ├── base.html├── templates/├── .env.example├── README.md├── requirements.txt├── app.py│EcoReminder```## 🗂️ Project Structure  - password: `admin123`  - username: `admin`- **Admin** (created on first run):## 🧩 AccountsThe application will be available at: **http://127.0.0.1:5000**```flask runset FLASK_ENV=developmentset FLASK_APP=app.py```bash### 5) Run the app3. Copy `.env.example` to `.env` and update values if needed.```CREATE DATABASE ecoreminder;```sql2. Create a database:1. Start MySQL (or MariaDB).### 4) Configure database```pip install -r requirements.txt```bash### 3) Install dependencies```.\.venv\Scripts\activatepython -m venv .venv```bash### 2) Create a Python virtual environment```cd c:\Users\HP\Desktop\Ecoremainder```bash### 1) Clone / open the project## 🚀 Quick Start- **Charts**: Chart.js- **Database**: MySQL- **Backend**: Python Flask- **Frontend**: HTML, CSS, JavaScript, Bootstrap## 🧰 Tech Stack- **Database**: MySQL-backed storage for users, collectors, complaints, and admins- **Analytics**: charts showing total/pending/completed reports- **Admin module**: secure admin login, view all complaints, assign collectors, monitor dashboard analytics- **Collector module**: login, view assigned complaints, accept tasks, update statuses, upload proof images- **Citizen module**: register/login, report full bins, upload images, track status, view history## ✅ FeaturesEcoReminder is a full-stack web application that enables citizens to report full garbage bins, allows officers to manage collections, and provides administrators with analytics and task assignment features.
EcoReminder is a full-stack web application built with **Python Flask**, **MySQL**, and **Bootstrap**. It helps citizens report full garbage bins, enables collectors to manage and update collections, and provides an admin dashboard with analytics.

---

## ✅ Features

### Citizen Module
- Register + login
- Submit a full dustbin report (location + photo)
- Track report status
- View history of complaints

### Garbage Collector Module
- Collector login
- View assigned complaints
- Accept tasks
- Update status (Pending → In Progress → Collected)
- Upload proof image after collection

### Admin Module
- Secure admin login
- View all complaints
- Assign complaints to collectors
- Monitor status counts and chart analytics

---

## 🧱 Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Charts:** Chart.js

---

## 🚀 Setup (Local Development)

### 1) Clone / open this repository in VS Code

### 2) Create a Python virtual environment

```bash
python -m venv .venv
```

### 3) Activate the venv

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**

```cmd
.\.venv\Scripts\activate.bat
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Setup the database

1. Start MySQL service.
2. Create a database:

```sql
CREATE DATABASE ecoreminder;
```

3. Update `.env` using `.env.example` values.

### 6) Configure environment variables

Copy the example file:

```bash
copy .env.example .env
```

Update `.env` values as needed (DB credentials, secret key).

### 7) Run the app

```bash
python app.py
```

Then open: http://127.0.0.1:5000

---

## 🔐 Default Admin Credentials

When the app starts, it seeds a default admin user (if none exists):

- **username:** `admin`
- **password:** `admin123`

> ⚠️ Change this password immediately in production.

---

## 🗂️ Project Structure

```
EcoReminder/
├── app.py
├── requirements.txt
├── templates/
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── base.html
│   ├── citizen_dashboard.html
│   ├── collector_dashboard.html
│   ├── collector_login.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── report.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── .env.example
```

---

## 🧩 Notes

- Uploaded images are saved to `static/images/uploads/`.
- Status chart uses Chart.js (included via CDN).
- You can customize styling in `static/css/style.css`.

Enjoy building a cleaner city with EcoReminder! 🌍
