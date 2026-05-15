import bcrypt
import jwt

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.accounts.models import UserSession


MAX_BCRYPT_PASSWORD_BYTES = 72


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_password_for_bcrypt(password: str) -> None:
    if not password:
        raise ValueError("Password is required.")

    if len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password is too long for bcrypt. Maximum is 72 bytes.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")


def hash_password(password: str) -> str:
    validate_password_for_bcrypt(password)

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def get_client_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR", "")


def create_user_session(user, request) -> UserSession:
    expires_at = timezone.now() + timedelta(hours=settings.JWT_EXPIRE_HOURS)

    return UserSession.objects.create(
        user=user,
        expires_at=expires_at,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        ip_address=get_client_ip(request),
    )


def create_access_token(user, session: UserSession) -> str:
    now = timezone.now()

    payload = {
        "sub": str(user.id),
        "jti": str(session.token_jti),
        "iat": int(now.timestamp()),
        "exp": int(session.expires_at.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require": ["sub", "jti", "iat", "exp"],
        },
    )