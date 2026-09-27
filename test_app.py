import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.app import activities, app


class TeacherAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.participants = list(activities["Chess Club"]["participants"])
        self.credentials = patch.dict(
            os.environ,
            {"TEACHER_USERNAME": "teacher", "TEACHER_PASSWORD": "test-password"},
        )
        self.credentials.start()

    def tearDown(self):
        activities["Chess Club"]["participants"][:] = self.participants
        self.credentials.stop()

    def test_activity_view_is_public(self):
        response = self.client.get("/activities")

        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_mutations_are_rejected_without_changes(self):
        signup = self.client.post(
            "/activities/Chess Club/signup", params={"email": "new@mergington.edu"}
        )
        unregister = self.client.delete(
            "/activities/Chess Club/unregister",
            params={"email": self.participants[0]},
        )

        self.assertEqual(signup.status_code, 401)
        self.assertEqual(unregister.status_code, 401)
        self.assertEqual(activities["Chess Club"]["participants"], self.participants)

    def test_teacher_can_verify_and_manage_signups(self):
        auth = ("teacher", "test-password")
        login = self.client.get("/auth/teacher", auth=auth)
        signup = self.client.post(
            "/activities/Chess Club/signup",
            params={"email": "new@mergington.edu"},
            auth=auth,
        )
        unregister = self.client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "new@mergington.edu"},
            auth=auth,
        )

        self.assertEqual(login.status_code, 200)
        self.assertEqual(signup.status_code, 200)
        self.assertEqual(unregister.status_code, 200)


if __name__ == "__main__":
    unittest.main()