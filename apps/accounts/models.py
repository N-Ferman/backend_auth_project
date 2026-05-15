import uuid

from django.db import models
from django.utils import timezone


class User(models.Model):
    email = models.EmailField(unique=True)

    password_hash = models.TextField()

    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, default="")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email


class UserSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    token_jti = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    user_agent = models.TextField(blank=True, default="")
    ip_address = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        db_table = "sessions"

    def __str__(self):
        return f"Session {self.token_jti} for {self.user.email}"
