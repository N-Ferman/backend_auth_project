from rest_framework.response import Response
from rest_framework import status

from apps.accounts.views import BaseAPIView
from apps.access.models import (
    Role,
    UserRole,
    BusinessElement,
    AccessRoleRule,
)
from apps.access.serializers import (
    RoleSerializer,
    BusinessElementSerializer,
    AccessRoleRuleSerializer,
    UserRoleSerializer,
)


class RoleListCreateView(BaseAPIView):
    def get(self, request):
        self.require_admin(request)

        roles = Role.objects.all().order_by("id")

        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        self.require_admin(request)

        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.save()

        return Response(
            RoleSerializer(role).data,
            status=status.HTTP_201_CREATED,
        )


class RoleDetailView(BaseAPIView):
    def get(self, request, role_id):
        self.require_admin(request)

        role = Role.objects.get(id=role_id)

        return Response(RoleSerializer(role).data)

    def patch(self, request, role_id):
        self.require_admin(request)

        role = Role.objects.get(id=role_id)

        serializer = RoleSerializer(
            role,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        role = serializer.save()

        return Response(RoleSerializer(role).data)

    def delete(self, request, role_id):
        self.require_admin(request)

        role = Role.objects.get(id=role_id)
        role.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessElementListCreateView(BaseAPIView):
    def get(self, request):
        self.require_admin(request)

        elements = BusinessElement.objects.all().order_by("id")

        return Response(BusinessElementSerializer(elements, many=True).data)

    def post(self, request):
        self.require_admin(request)

        serializer = BusinessElementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        element = serializer.save()

        return Response(
            BusinessElementSerializer(element).data,
            status=status.HTTP_201_CREATED,
        )


class AccessRuleListCreateView(BaseAPIView):
    def get(self, request):
        self.require_admin(request)

        rules = (
            AccessRoleRule.objects
            .select_related("role", "element")
            .all()
            .order_by("role_id", "element_id")
        )

        return Response(AccessRoleRuleSerializer(rules, many=True).data)

    def post(self, request):
        self.require_admin(request)

        serializer = AccessRoleRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rule = serializer.save()

        return Response(
            AccessRoleRuleSerializer(rule).data,
            status=status.HTTP_201_CREATED,
        )


class AccessRuleDetailView(BaseAPIView):
    def get(self, request, rule_id):
        self.require_admin(request)

        rule = (
            AccessRoleRule.objects
            .select_related("role", "element")
            .get(id=rule_id)
        )

        return Response(AccessRoleRuleSerializer(rule).data)

    def patch(self, request, rule_id):
        self.require_admin(request)

        rule = AccessRoleRule.objects.get(id=rule_id)

        serializer = AccessRoleRuleSerializer(
            rule,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        rule = serializer.save()

        return Response(AccessRoleRuleSerializer(rule).data)

    def delete(self, request, rule_id):
        self.require_admin(request)

        rule = AccessRoleRule.objects.get(id=rule_id)
        rule.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleListCreateView(BaseAPIView):
    def get(self, request):
        self.require_admin(request)

        user_roles = (
            UserRole.objects
            .select_related("user", "role")
            .all()
            .order_by("user_id", "role_id")
        )

        return Response(UserRoleSerializer(user_roles, many=True).data)

    def post(self, request):
        self.require_admin(request)

        serializer = UserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_role = serializer.save()

        return Response(
            UserRoleSerializer(user_role).data,
            status=status.HTTP_201_CREATED,
        )


class UserRoleDetailView(BaseAPIView):
    def delete(self, request, user_role_id):
        self.require_admin(request)

        user_role = UserRole.objects.get(id=user_role_id)
        user_role.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
