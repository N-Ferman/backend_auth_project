import jwt

from django.utils import timezone

from apps.accounts.models import UserSession
from apps.accounts.services import decode_access_token


class CustomJWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.auth_user = None
        request.auth_session = None
        request.auth_error = None

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "", 1).strip()

            try:
                payload = decode_access_token(token)

                token_jti = payload.get("jti")
                user_id = payload.get("sub")

                session = (
                    UserSession.objects
                    .select_related("user")
                    .filter(
                        token_jti=token_jti,
                        user_id=user_id,
                        is_active=True,
                    )
                    .first()
                )

                if session is None:
                    request.auth_error = "Session not found or inactive."

                elif session.expires_at <= timezone.now():
                    session.is_active = False
                    session.save(update_fields=["is_active"])
                    request.auth_error = "Session expired."

                elif not session.user.is_active:
                    request.auth_error = "User is inactive."

                else:
                    request.auth_user = session.user
                    request.auth_session = session

            except jwt.ExpiredSignatureError:
                request.auth_error = "Token expired."

            except jwt.InvalidTokenError:
                request.auth_error = "Invalid token."

            except Exception:
                request.auth_error = "Authentication error."

        return self.get_response(request)