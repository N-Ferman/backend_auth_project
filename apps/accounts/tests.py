from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services import hash_password
from apps.access.models import Role, UserRole


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_role = Role.objects.create(
            code="user",
            name="User",
            description="Default user role",
        )

        self.user = User.objects.create(
            email="user@example.com",
            password_hash=hash_password("User12345!"),
            last_name="Userov",
            first_name="User",
            patronymic="",
            is_active=True,
        )

        UserRole.objects.create(
            user=self.user,
            role=self.user_role,
        )

    def test_register_user_successfully(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new@example.com",
                "password": "NewUser12345!",
                "password_repeat": "NewUser12345!",
                "last_name": "New",
                "first_name": "User",
                "patronymic": "Test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "new@example.com")
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_register_with_different_passwords_returns_400(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new@example.com",
                "password": "NewUser12345!",
                "password_repeat": "Different12345!",
                "last_name": "New",
                "first_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_successfully(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "User12345!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.data)
        self.assertEqual(response.data["token_type"], "Bearer")

    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_me_without_token_returns_401(self):
        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, 401)

    def test_me_with_token_returns_user(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "User12345!",
            },
            format="json",
        )

        token = login_response.data["access_token"]

        response = self.client.get(
            "/api/me/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "user@example.com")

    def test_logout_makes_token_invalid(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "User12345!",
            },
            format="json",
        )

        token = login_response.data["access_token"]

        logout_response = self.client.post(
            "/api/auth/logout/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(logout_response.status_code, 200)

        me_response = self.client.get(
            "/api/me/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(me_response.status_code, 401)

    def test_soft_delete_user(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "User12345!",
            },
            format="json",
        )

        token = login_response.data["access_token"]

        delete_response = self.client.delete(
            "/api/me/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(delete_response.status_code, 200)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.deleted_at)

    def test_login_after_soft_delete_returns_401(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "user@example.com",
                "password": "User12345!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
