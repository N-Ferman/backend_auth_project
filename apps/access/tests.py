from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services import hash_password
from apps.access.models import (
    Role,
    UserRole,
    BusinessElement,
    AccessRoleRule,
)


class AccessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_role = Role.objects.create(
            code="admin",
            name="Admin",
        )

        self.user_role = Role.objects.create(
            code="user",
            name="User",
        )

        self.access_element = BusinessElement.objects.create(
            code="access_rules",
            name="Access rules",
        )

        AccessRoleRule.objects.create(
            role=self.admin_role,
            element=self.access_element,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )

        self.admin = User.objects.create(
            email="admin@example.com",
            password_hash=hash_password("Admin12345!"),
            last_name="Adminov",
            first_name="Admin",
            is_active=True,
        )

        self.user = User.objects.create(
            email="user@example.com",
            password_hash=hash_password("User12345!"),
            last_name="Userov",
            first_name="User",
            is_active=True,
        )

        UserRole.objects.create(
            user=self.admin,
            role=self.admin_role,
        )

        UserRole.objects.create(
            user=self.user,
            role=self.user_role,
        )

    def login(self, email, password):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": email,
                "password": password,
            },
            format="json",
        )

        return response.data["access_token"]

    def test_admin_can_get_access_rules(self):
        token = self.login("admin@example.com", "Admin12345!")

        response = self.client.get(
            "/api/admin/rules/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_get_access_rules(self):
        token = self.login("user@example.com", "User12345!")

        response = self.client.get(
            "/api/admin/rules/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_gets_401(self):
        response = self.client.get("/api/admin/rules/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_role(self):
        token = self.login("admin@example.com", "Admin12345!")

        response = self.client.post(
            "/api/admin/roles/",
            {
                "code": "editor",
                "name": "Editor",
                "description": "Can edit content",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Role.objects.filter(code="editor").exists())
