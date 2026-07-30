import os
import sqlite3
import uuid
from datetime import datetime

import bcrypt
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

# ---- Configuration ----
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "images", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ecoreminder-secret-key-2026")
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
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def parse_row(row):
    if not row:
        return None
    d = dict(row)
    if "created_at" in d and d["created_at"]:
        if isinstance(d["created_at"], str):
            try:
                # Handle possible fractional seconds or ISO format
                clean_date = d["created_at"].split(".")[0].replace("T", " ")
                d["created_at"] = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
    return d


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
            phone TEXT,
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
            latitude REAL,
            longitude REAL,
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

    # Migrations for existing databases
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "latitude" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN latitude REAL")
    if "longitude" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN longitude REAL")

    cursor.execute("PRAGMA table_info(collectors)")
    collector_cols = [row["name"] for row in cursor.fetchall()]
    if "phone" not in collector_cols:
        cursor.execute("ALTER TABLE collectors ADD COLUMN phone TEXT")

    # Insert default admin if not exist
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        password = hash_password("admin123")
        cursor.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            ("admin", password),
        )
        print("Seeded default admin -> username: admin | password: admin123")

    # Insert sample collector if empty
    cursor.execute("SELECT COUNT(*) FROM collectors")
    if cursor.fetchone()[0] == 0:
        pwd_collector = hash_password("collector123")
        cursor.execute(
            "INSERT INTO collectors (name, email, password, phone) VALUES (?, ?, ?, ?)",
            ("John Sanitation", "john@ecoreminder.com", pwd_collector, "+1 555-0192"),
        )
        cursor.execute(
            "INSERT INTO collectors (name, email, password, phone) VALUES (?, ?, ?, ?)",
            ("Sarah EcoClean", "sarah@ecoreminder.com", pwd_collector, "+1 555-0193"),
        )
        print("Seeded sample collectors -> john@ecoreminder.com & sarah@ecoreminder.com (password: collector123)")

    # Insert sample citizen user if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        pwd_user = hash_password("citizen123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Alex Green", "citizen@ecoreminder.com", pwd_user),
        )
        user_id = cursor.lastrowid
        print("Seeded sample citizen -> citizen@ecoreminder.com (password: citizen123)")

        # Seed sample complaints with latitude/longitude
        sample_complaints = [
            (user_id, "Central Park Gate 3, High Street", 40.7829, -73.9654, "Dustbin overflowing with organic waste.", "Pending", None),
            (user_id, "Market Square North, Plaza 12", 40.7589, -73.9851, "Recycling bin severely full and plastic spilling.", "In Progress", 1),
            (user_id, "Metro Station Exit B", 40.7484, -73.9857, "Bin cleared successfully by morning crew.", "Collected", 2),
        ]
        for u_id, loc, lat, lng, desc, stat, collector_id in sample_complaints:
            cursor.execute(
                "INSERT INTO complaints (user_id, location, latitude, longitude, description, status, assigned_collector) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (u_id, loc, lat, lng, desc, stat, collector_id),
            )
        print("Seeded sample dustbin complaints with geo-coordinates.")

    conn.commit()
    cursor.close()
    conn.close()


def is_logged_in():
    return session.get("role") in {"citizen", "collector", "admin"} and session.get("user_id")


@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Collected'")
    total_collected = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM collectors")
    total_collectors = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        total_complaints=total_complaints,
        total_collected=total_collected,
        total_collectors=total_collectors,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not (name and email and password and confirm):
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
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
            flash("Registration successful! Please login to report full dustbins.", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as err:
            if "UNIQUE constraint failed" in str(err):
                flash("Email is already registered. Please login.", "warning")
            else:
                flash("Error creating account: %s" % err, "danger")
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
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("citizen_dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/report", methods=["GET", "POST"])
def report():
    if session.get("role") != "citizen":
        flash("Please login as a citizen to submit a report.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        lat_val = request.form.get("latitude", "").strip()
        lng_val = request.form.get("longitude", "").strip()

        latitude = float(lat_val) if lat_val else None
        longitude = float(lng_val) if lng_val else None

        file = request.files.get("image")
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        if not location:
            flash("Please specify a location address or pick on map.", "warning")
            return redirect(url_for("report"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complaints (user_id, location, latitude, longitude, description, image) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], location, latitude, longitude, description, filename),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Dustbin report submitted successfully! Sanitation team notified.", "success")
        return redirect(url_for("citizen_dashboard"))

    return render_template("report.html")


@app.route("/citizen/dashboard")
def citizen_dashboard():
    if session.get("role") != "citizen":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, co.name AS collector_name, co.phone AS collector_phone
        FROM complaints c
        LEFT JOIN collectors co ON c.assigned_collector = co.id
        WHERE c.user_id=?
        ORDER BY c.created_at DESC
        """,
        (session["user_id"],),
    )
    rows = cursor.fetchall()
    complaints = [parse_row(r) for r in rows]

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
            flash(f"Welcome, Collector {collector['name']}!", "success")
            return redirect(url_for("collector_dashboard"))

        flash("Invalid collector email or password.", "danger")
        return redirect(url_for("collector_login"))

    return render_template("collector_login.html")


@app.route("/collector/dashboard")
def collector_dashboard():
    if session.get("role") != "collector":
        return redirect(url_for("collector_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, u.name AS citizen_name, u.email AS citizen_email
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.assigned_collector=?
        ORDER BY c.created_at DESC
        """,
        (session["user_id"],),
    )
    rows = cursor.fetchall()
    complaints = [parse_row(r) for r in rows]

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
        "UPDATE complaints SET assigned_collector=?, status='In Progress', updated_at=CURRENT_TIMESTAMP WHERE complaint_id=?",
        (session["user_id"], complaint_id),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Collection task accepted! Status set to 'In Progress'.", "success")
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
    sql = "UPDATE complaints SET status=?, updated_at=CURRENT_TIMESTAMP"
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

    flash("Task status updated successfully.", "success")
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
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Summary metrics
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
    in_progress = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Collected'")
    collected = cursor.fetchone()[0]

    # Complaints list
    cursor.execute(
        """
        SELECT c.*, u.name AS user_name, co.name AS collector_name
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN collectors co ON c.assigned_collector = co.id
        ORDER BY c.created_at DESC
        """
    )
    rows = cursor.fetchall()
    complaints = [parse_row(r) for r in rows]

    # Collectors list with assignment count
    cursor.execute(
        """
        SELECT co.*, COUNT(c.complaint_id) AS active_tasks
        FROM collectors co
        LEFT JOIN complaints c ON co.id = c.assigned_collector AND c.status != 'Collected'
        GROUP BY co.id
        ORDER BY co.name
        """
    )
    collector_rows = cursor.fetchall()
    collectors = [dict(c) for c in collector_rows]

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=pending,
        in_progress=in_progress,
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
        flash("Please select both a complaint and a collector.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET assigned_collector=?, status='In Progress', updated_at=CURRENT_TIMESTAMP WHERE complaint_id=?",
        (collector_id, complaint_id),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Complaint assigned to collector successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/collectors/add", methods=["POST"])
def admin_add_collector():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    phone = request.form.get("phone", "").strip()

    if not (name and email and password):
        flash("Name, email, and password are required to create a collector.", "warning")
        return redirect(url_for("admin_dashboard"))

    hashed = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO collectors (name, email, password, phone) VALUES (?, ?, ?, ?)",
            (name, email, hashed, phone),
        )
        conn.commit()
        flash(f"Collector account created for {name}.", "success")
    except sqlite3.Error as err:
        if "UNIQUE constraint failed" in str(err):
            flash("Collector with this email already exists.", "warning")
        else:
            flash("Error creating collector: %s" % err, "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/collectors/delete/<int:collector_id>", methods=["POST"])
def admin_delete_collector(collector_id):
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    # Unassign complaints
    cursor.execute("UPDATE complaints SET assigned_collector=NULL WHERE assigned_collector=?", (collector_id,))
    cursor.execute("DELETE FROM collectors WHERE id=?", (collector_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Collector account removed.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/api/complaints")
def api_complaints():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_role = session.get("role")
    user_id = session.get("user_id")

    if user_role == "citizen":
        cursor.execute(
            """
            SELECT c.complaint_id, c.location, c.latitude, c.longitude, c.status, c.description, c.image, c.proof_image, c.created_at
            FROM complaints c WHERE c.user_id=?
            """,
            (user_id,),
        )
    elif user_role == "collector":
        cursor.execute(
            """
            SELECT c.complaint_id, c.location, c.latitude, c.longitude, c.status, c.description, c.image, c.proof_image, c.created_at
            FROM complaints c WHERE c.assigned_collector=?
            """,
            (user_id,),
        )
    else:
        cursor.execute(
            """
            SELECT c.complaint_id, c.location, c.latitude, c.longitude, c.status, c.description, c.image, c.proof_image, c.created_at,
                   u.name AS user_name, co.name AS collector_name
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN collectors co ON c.assigned_collector = co.id
            """
        )

    rows = cursor.fetchall()
    result = []
    for r in rows:
        item = parse_row(r)
        if item.get("created_at") and isinstance(item["created_at"], datetime):
            item["created_at"] = item["created_at"].strftime("%Y-%m-%d %H:%M")
        result.append(item)

    cursor.close()
    conn.close()
    return jsonify(result)


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    init_db()
    print("EcoReminder initialized successfully.")
    app.run(debug=True, port=5000)
