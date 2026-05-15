from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.services import normalize_email, validate_password_for_bcrypt


class UserPublicSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "last_name",
            "first_name",
            "patronymic",
            "is_active",
            "created_at",
            "updated_at",
            "roles",
        ]

    def get_roles(self, obj):
        return [
            user_role.role.code
            for user_role in obj.user_roles.select_related("role").all()
        ]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    last_name = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    patronymic = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value):
        email = normalize_email(value)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists.")

        return email

    def validate(self, attrs):
        password = attrs.get("password")
        password_repeat = attrs.get("password_repeat")

        if password != password_repeat:
            raise serializers.ValidationError({
                "password_repeat": "Passwords do not match."
            })

        try:
            validate_password_for_bcrypt(password)
        except ValueError as exc:
            raise serializers.ValidationError({
                "password": str(exc)
            })

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UpdateProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    patronymic = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value):
        email = normalize_email(value)
        user = self.context["user"]

        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise serializers.ValidationError("User with this email already exists.")

        return email