import os
import sqlite3
import uuid
from datetime import datetime

import bcrypt
from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

# ---- Configuration ----
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "images", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.context_processor
def inject_global_vars():
    return {"current_year": datetime.now().year}


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables if not exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS collectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            image TEXT,
            status TEXT DEFAULT 'Pending',
            assigned_collector INTEGER,
            proof_image TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_collector) REFERENCES collectors(id) ON DELETE SET NULL
        )
        """
    )

    # Insert default admin if not exist
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        password = hash_password("admin123")
        cursor.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            ("admin", password),
        )
        print("Created default admin credentials -> username: admin password: admin123")

    conn.commit()
    cursor.close()
    conn.close()


def is_logged_in():
    return session.get("role") in {"citizen", "collector", "admin"} and session.get("user_id")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not (name and email and password and confirm):
            flash("Please fill all fields", "warning")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        hashed = hash_password(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed),
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as err:
            if "UNIQUE constraint failed" in str(err):
                flash("Email already registered", "warning")
            else:
                flash("Something went wrong: %s" % err, "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password(password, user["password"]):
            session.clear()
            session["user_id"] = user["id"]
            session["role"] = "citizen"
            session["name"] = user["name"]
            return redirect(url_for("citizen_dashboard"))

        flash("Invalid email or password", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))


@app.route("/report", methods=["GET", "POST"])
def report():
    if session.get("role") != "citizen":
        flash("Please login as a citizen to report.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("image")
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        if not location:
            flash("Please enter a location", "warning")
            return redirect(url_for("report"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complaints (user_id, location, description, image) VALUES (?, ?, ?, ?)",
            (session["user_id"], location, description, filename),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Complaint submitted successfully", "success")
        return redirect(url_for("citizen_dashboard"))

    return render_template("report.html")


@app.route("/citizen/dashboard")
def citizen_dashboard():
    if session.get("role") != "citizen":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM complaints WHERE user_id=? ORDER BY created_at DESC", (session["user_id"],)
    )
    complaints = cursor.fetchall()
    for c in complaints:
        c['created_at'] = datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S')
    cursor.close()
    conn.close()

    return render_template("citizen_dashboard.html", complaints=complaints)


@app.route("/collector/login", methods=["GET", "POST"])
def collector_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM collectors WHERE email=?", (email,))
        collector = cursor.fetchone()
        cursor.close()
        conn.close()

        if collector and check_password(password, collector["password"]):
            session.clear()
            session["user_id"] = collector["id"]
            session["role"] = "collector"
            session["name"] = collector["name"]
            return redirect(url_for("collector_dashboard"))

        flash("Invalid email or password", "danger")
        return redirect(url_for("collector_login"))

    return render_template("collector_login.html")


@app.route("/collector/dashboard")
def collector_dashboard():
    if session.get("role") != "collector":
        return redirect(url_for("collector_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM complaints WHERE assigned_collector=? ORDER BY created_at DESC", (session["user_id"],)
    )
    complaints = cursor.fetchall()
    for c in complaints:
        c['created_at'] = datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S')
    cursor.close()
    conn.close()

    return render_template("collector_dashboard.html", complaints=complaints)


@app.route("/collector/accept/<int:complaint_id>")
def collector_accept(complaint_id):
    if session.get("role") != "collector":
        return redirect(url_for("collector_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET assigned_collector=?, status='In Progress' WHERE complaint_id=?", 
        (session["user_id"], complaint_id),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Task accepted", "success")
    return redirect(url_for("collector_dashboard"))


@app.route("/collector/update/<int:complaint_id>", methods=["POST"])
def collector_update(complaint_id):
    if session.get("role") != "collector":
        return redirect(url_for("collector_login"))

    status = request.form.get("status")
    file = request.files.get("proof_image")
    filename = None

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE complaints SET status=?"
    params = [status]
    if filename:
        sql += ", proof_image=?"
        params.append(filename)
    sql += " WHERE complaint_id=? AND assigned_collector=?"
    params.extend([complaint_id, session["user_id"]])
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()

    flash("Status updated", "success")
    return redirect(url_for("collector_dashboard"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username=?", (username,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin and check_password(password, admin["password"]):
            session.clear()
            session["user_id"] = admin["id"]
            session["role"] = "admin"
            session["name"] = admin["username"]
            return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Summary counts
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Collected'")
    collected = cursor.fetchone()[0]

    # Complaints list
    cursor.execute(
        "SELECT c.*, u.name AS user_name, co.name AS collector_name FROM complaints c "
        "LEFT JOIN users u ON c.user_id=u.id "
        "LEFT JOIN collectors co ON c.assigned_collector=co.id "
        "ORDER BY c.created_at DESC"
    )
    complaints = cursor.fetchall()
    for c in complaints:
        c['created_at'] = datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S')

    # Collectors list
    cursor.execute("SELECT id, name FROM collectors ORDER BY name")
    collectors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=pending,
        collected=collected,
        complaints=complaints,
        collectors=collectors,
    )


@app.route("/admin/assign", methods=["POST"])
def admin_assign():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    complaint_id = request.form.get("complaint_id")
    collector_id = request.form.get("collector_id")

    if not complaint_id or not collector_id:
        flash("Please choose complaint and collector", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET assigned_collector=?, status='In Progress' WHERE complaint_id=?",
        (collector_id, complaint_id),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Assigned complaint to collector", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print("Failed to initialize database:", e)
        print("Please ensure MySQL is running and credentials are correct in .env file.")
        exit(1)
    app.run(debug=True)
