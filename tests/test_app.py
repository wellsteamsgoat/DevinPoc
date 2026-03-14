import unittest

from app import app


class TestHelloWorld(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_hello_world_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_hello_world_message(self):
        response = self.client.get("/")
        data = response.get_json()
        self.assertEqual(data["message"], "Hello, World!")

    def test_health_status_code(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_health_response(self):
        response = self.client.get("/health")
        data = response.get_json()
        self.assertEqual(data["status"], "ok")

    def test_not_found(self):
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
