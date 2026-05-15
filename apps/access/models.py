from django.db import models
from django.utils import timezone

from apps.accounts.models import User


class Role(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.code


class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            )
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.role.code}"


class BusinessElement(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "business_elements"

    def __str__(self):
        return self.code


class AccessRoleRule(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="access_rules",
    )

    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name="access_rules",
    )

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)

    create_permission = models.BooleanField(default=False)

    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)

    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "access_role_rules"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "element"],
                name="unique_role_element_rule",
            )
        ]

    def __str__(self):
        return f"{self.role.code} -> {self.element.code}"