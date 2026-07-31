"""
EcoReminder Database Module Unit Tests
"""

import unittest
from db import get_db_connection, fetch_complaint_counts, parse_row, hash_password, check_password
from app import init_db


class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_password_hashing(self):
        pwd = "securepassword123"
        hashed = hash_password(pwd)
        self.assertTrue(check_password(pwd, hashed))
        self.assertFalse(check_password("wrongpassword", hashed))

    def test_parse_row_date_conversion(self):
        mock_row = {"created_at": "2026-07-31 12:00:00.123456", "location": "Main St"}
        parsed = parse_row(mock_row)
        self.assertEqual(parsed["location"], "Main St")

    def test_fetch_complaint_counts(self):
        total, pending, in_progress, collected = fetch_complaint_counts()
        self.assertGreaterEqual(total, 0)
        self.assertEqual(total, pending + in_progress + collected)


if __name__ == "__main__":
    unittest.main()
