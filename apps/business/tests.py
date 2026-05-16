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


class BusinessApiTests(TestCase):
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

        self.products = BusinessElement.objects.create(
            code="products",
            name="Products",
        )

        self.orders = BusinessElement.objects.create(
            code="orders",
            name="Orders",
        )

        AccessRoleRule.objects.create(
            role=self.admin_role,
            element=self.products,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )

        AccessRoleRule.objects.create(
            role=self.admin_role,
            element=self.orders,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )

        AccessRoleRule.objects.create(
            role=self.user_role,
            element=self.products,
            read_permission=True,
            read_all_permission=True,
            create_permission=False,
        )

        AccessRoleRule.objects.create(
            role=self.user_role,
            element=self.orders,
            read_permission=True,
            read_all_permission=False,
            create_permission=True,
            update_permission=True,
            delete_permission=True,
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

    def test_user_can_read_products(self):
        token = self.login("user@example.com", "User12345!")

        response = self.client.get(
            "/api/business/products/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["scope"], "all")
        self.assertGreater(len(response.data["items"]), 0)

    def test_user_can_read_only_own_orders(self):
        token = self.login("user@example.com", "User12345!")

        response = self.client.get(
            "/api/business/orders/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["scope"], "own")

        for item in response.data["items"]:
            self.assertEqual(item["owner_id"], self.user.id)

    def test_user_cannot_create_product(self):
        token = self.login("user@example.com", "User12345!")

        response = self.client.post(
            "/api/business/products/",
            {
                "title": "New product",
                "price": 100,
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_user_can_create_order(self):
        token = self.login("user@example.com", "User12345!")

        response = self.client.post(
            "/api/business/orders/",
            {
                "title": "New order",
                "status": "created",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["object"]["owner_id"], self.user.id)

    def test_unauthorized_business_request_returns_401(self):
        response = self.client.get("/api/business/products/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_read_all_orders(self):
        token = self.login("admin@example.com", "Admin12345!")

        response = self.client.get(
            "/api/business/orders/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["scope"], "all")
