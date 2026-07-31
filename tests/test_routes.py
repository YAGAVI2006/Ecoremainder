"""
EcoReminder Route Integration Tests (Unittest & Pytest compatible)
"""

import unittest
from app import app, init_db


class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        init_db()
        self.client = app.test_client()

    def test_index_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"EcoReminder", res.data)

    def test_citizen_login_page(self):
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Citizen Login", res.data)

    def test_collector_login_page(self):
        res = self.client.get("/collector/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Collector Portal Login", res.data)

    def test_admin_login_page(self):
        res = self.client.get("/admin/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Portal", res.data)

    def test_api_complaints_endpoint(self):
        res = self.client.get("/api/complaints")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.is_json)


if __name__ == "__main__":
    unittest.main()
