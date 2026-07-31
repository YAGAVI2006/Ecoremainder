"""
EcoReminder Demo Seed Generator
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db_connection, hash_password
from app import init_db


def seed_demo_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    if not user:
        pwd = hash_password("citizen123")
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", ("Demo Citizen", "citizen@ecoreminder.com", pwd))
        user_id = cursor.lastrowid
    else:
        user_id = user["id"]

    demo_reports = [
        (user_id, "7th Avenue Corner", 40.7549, -73.9840, "Recycling bin full", "Pending", "High"),
        (user_id, "Broadway Theater District", 40.7590, -73.9845, "Overflowing trash bin", "In Progress", "Critical"),
        (user_id, "Hudson River Park Walkway", 40.7420, -74.0090, "Compost bin full", "Collected", "Low"),
    ]

    for u_id, loc, lat, lng, desc, status, priority in demo_reports:
        cursor.execute(
            """
            INSERT INTO complaints (user_id, location, latitude, longitude, description, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (u_id, loc, lat, lng, desc, status, priority),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Successfully seeded additional demo dustbin reports.")


if __name__ == "__main__":
    seed_demo_data()
