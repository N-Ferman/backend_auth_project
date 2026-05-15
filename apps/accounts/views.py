from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.exceptions import UnauthorizedError, ForbiddenError
from apps.accounts.models import User
from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UpdateProfileSerializer,
    UserPublicSerializer,
)
from apps.accounts.services import (
    hash_password,
    check_password,
    normalize_email,
    create_user_session,
    create_access_token,
)
from apps.access.models import Role, UserRole


class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get_current_user(self, request):
        user = getattr(request, "auth_user", None)

        if user is None and hasattr(request, "_request"):
            user = getattr(request._request, "auth_user", None)

        if user is None:
            raise UnauthorizedError("User is not authenticated.")

        return user

    def get_current_session(self, request):
        session = getattr(request, "auth_session", None)

        if session is None and hasattr(request, "_request"):
            session = getattr(request._request, "auth_session", None)

        if session is None:
            raise UnauthorizedError("Session is not authenticated.")

        return session

    def require_admin(self, request):
        user = self.get_current_user(request)

        has_admin_role = user.user_roles.filter(role__code="admin").exists()

        if not has_admin_role:
            raise ForbiddenError("Admin role is required.")

        return user


class RegisterView(BaseAPIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        with transaction.atomic():
            user = User.objects.create(
                email=data["email"],
                password_hash=hash_password(data["password"]),
                last_name=data["last_name"],
                first_name=data["first_name"],
                patronymic=data.get("patronymic", ""),
            )

            default_role, _ = Role.objects.get_or_create(
                code="user",
                defaults={
                    "name": "User",
                    "description": "Default registered user",
                },
            )

            UserRole.objects.create(
                user=user,
                role=default_role,
            )

        return Response(
            UserPublicSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(BaseAPIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = normalize_email(serializer.validated_data["email"])
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise UnauthorizedError("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive.")

        if not check_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        session = create_user_session(user, request)
        token = create_access_token(user, session)

        return Response({
            "access_token": token,
            "token_type": "Bearer",
            "expires_at": session.expires_at,
            "user": UserPublicSerializer(user).data,
        })


class LogoutView(BaseAPIView):
    def post(self, request):
        session = self.get_current_session(request)

        session.is_active = False
        session.save(update_fields=["is_active"])

        return Response({
            "detail": "Successfully logged out."
        })


class MeView(BaseAPIView):
    def get(self, request):
        user = self.get_current_user(request)

        return Response(UserPublicSerializer(user).data)

    def patch(self, request):
        user = self.get_current_user(request)

        serializer = UpdateProfileSerializer(
            data=request.data,
            context={"user": user},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(user, field, value)

        user.save()

        return Response(UserPublicSerializer(user).data)

    def delete(self, request):
        user = self.get_current_user(request)

        user.is_active = False
        user.deleted_at = timezone.now()
        user.save(update_fields=["is_active", "deleted_at", "updated_at"])

        user.sessions.filter(is_active=True).update(is_active=False)

        return Response({
            "detail": "Account was deleted softly."
        })
