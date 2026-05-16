from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.accounts.services import hash_password
from apps.access.models import (
    Role,
    UserRole,
    BusinessElement,
    AccessRoleRule,
)


class Command(BaseCommand):
    help = "Seed demo users, roles, business elements and access rules."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.create_roles()
            self.create_elements()
            self.create_users()
            self.create_rules()

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))

    def create_roles(self):
        roles = [
            ("admin", "Administrator", "Full access"),
            ("manager", "Manager", "Manager access"),
            ("user", "User", "Default user access"),
            ("guest", "Guest", "Limited user access"),
        ]

        for code, name, description in roles:
            Role.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                },
            )

    def create_elements(self):
        elements = [
            ("users", "Users", "Application users"),
            ("access_rules", "Access rules", "Roles, elements and permissions"),
            ("products", "Products", "Mock products"),
            ("orders", "Orders", "Mock orders"),
            ("stores", "Stores", "Mock stores"),
        ]

        for code, name, description in elements:
            BusinessElement.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                },
            )

    def create_demo_user(self, email, password, last_name, first_name, role_code):
        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                "password_hash": hash_password(password),
                "last_name": last_name,
                "first_name": first_name,
                "patronymic": "",
                "is_active": True,
                "deleted_at": None,
            },
        )

        role = Role.objects.get(code=role_code)

        UserRole.objects.get_or_create(
            user=user,
            role=role,
        )

        return user

    def create_users(self):
        self.create_demo_user(
            email="admin@example.com",
            password="Admin12345!",
            last_name="Adminov",
            first_name="Admin",
            role_code="admin",
        )

        self.create_demo_user(
            email="manager@example.com",
            password="Manager12345!",
            last_name="Managerov",
            first_name="Manager",
            role_code="manager",
        )

        self.create_demo_user(
            email="user@example.com",
            password="User12345!",
            last_name="Userov",
            first_name="User",
            role_code="user",
        )

        self.create_demo_user(
            email="guest@example.com",
            password="Guest12345!",
            last_name="Guestov",
            first_name="Guest",
            role_code="guest",
        )

    def set_rule(self, role_code, element_code, **permissions):
        role = Role.objects.get(code=role_code)
        element = BusinessElement.objects.get(code=element_code)

        defaults = {
            "read_permission": False,
            "read_all_permission": False,
            "create_permission": False,
            "update_permission": False,
            "update_all_permission": False,
            "delete_permission": False,
            "delete_all_permission": False,
        }

        defaults.update(permissions)

        AccessRoleRule.objects.update_or_create(
            role=role,
            element=element,
            defaults=defaults,
        )

    def create_rules(self):
        elements = BusinessElement.objects.all()

        for element in elements:
            self.set_rule(
                "admin",
                element.code,
                read_permission=True,
                read_all_permission=True,
                create_permission=True,
                update_permission=True,
                update_all_permission=True,
                delete_permission=True,
                delete_all_permission=True,
            )

        self.set_rule(
            "manager",
            "products",
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
        )

        self.set_rule(
            "manager",
            "orders",
            read_permission=True,
            read_all_permission=True,
            update_permission=True,
            update_all_permission=True,
        )

        self.set_rule(
            "manager",
            "stores",
            read_permission=True,
            read_all_permission=True,
        )

        self.set_rule(
            "user",
            "products",
            read_permission=True,
            read_all_permission=True,
        )

        self.set_rule(
            "user",
            "orders",
            read_permission=True,
            create_permission=True,
            update_permission=True,
            delete_permission=True,
        )

        self.set_rule(
            "user",
            "stores",
            read_permission=True,
            read_all_permission=True,
        )

        self.set_rule(
            "guest",
            "products",
            read_permission=True,
            read_all_permission=True,
        )

        self.set_rule(
            "guest",
            "stores",
            read_permission=True,
            read_all_permission=True,
        )