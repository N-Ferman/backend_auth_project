from rest_framework import serializers

from apps.access.models import (
    Role,
    UserRole,
    BusinessElement,
    AccessRoleRule,
)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = [
            "id",
            "code",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    element_code = serializers.CharField(source="element.code", read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = [
            "id",
            "role",
            "role_code",
            "element",
            "element_code",

            "read_permission",
            "read_all_permission",

            "create_permission",

            "update_permission",
            "update_all_permission",

            "delete_permission",
            "delete_all_permission",

            "created_at",
            "updated_at",
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)

    class Meta:
        model = UserRole
        fields = [
            "id",
            "user",
            "user_email",
            "role",
            "role_code",
            "created_at",
        ]