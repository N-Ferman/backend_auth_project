from rest_framework.response import Response
from rest_framework import status

from apps.accounts.exceptions import ForbiddenError
from apps.accounts.views import BaseAPIView
from apps.access.models import BusinessElement
from apps.access.services import (
    get_read_scope,
    can_create,
    can_read_object,
    can_update,
    can_delete,
)
from apps.business.mock_data import (
    build_mock_objects,
    find_mock_object,
)


class MockBusinessListCreateView(BaseAPIView):
    def get(self, request, element_code):
        user = self.get_current_user(request)

        if not BusinessElement.objects.filter(code=element_code).exists():
            return Response(
                {"detail": "Business element not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        scope = get_read_scope(user, element_code)

        if scope == "none":
            raise ForbiddenError("You do not have read access to this resource.")

        objects = build_mock_objects(element_code, user)

        if scope == "own":
            objects = [
                obj for obj in objects
                if int(obj["owner_id"]) == int(user.id)
            ]

        return Response({
            "element": element_code,
            "scope": scope,
            "items": objects,
        })

    def post(self, request, element_code):
        user = self.get_current_user(request)

        if not BusinessElement.objects.filter(code=element_code).exists():
            return Response(
                {"detail": "Business element not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_create(user, element_code):
            raise ForbiddenError("You do not have create access to this resource.")

        created_object = {
            "id": 999,
            "owner_id": user.id,
            **request.data,
        }

        return Response(
            {
                "detail": "Mock object created. It is not saved to DB.",
                "object": created_object,
            },
            status=status.HTTP_201_CREATED,
        )


class MockBusinessDetailView(BaseAPIView):
    def get(self, request, element_code, object_id):
        user = self.get_current_user(request)

        obj = find_mock_object(element_code, object_id, user)

        if obj is None:
            return Response(
                {"detail": "Mock object not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_read_object(user, element_code, obj["owner_id"]):
            raise ForbiddenError("You do not have read access to this object.")

        return Response(obj)

    def patch(self, request, element_code, object_id):
        user = self.get_current_user(request)

        obj = find_mock_object(element_code, object_id, user)

        if obj is None:
            return Response(
                {"detail": "Mock object not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_update(user, element_code, obj["owner_id"]):
            raise ForbiddenError("You do not have update access to this object.")

        updated_object = {
            **obj,
            **request.data,
        }

        return Response({
            "detail": "Mock object updated. It is not saved to DB.",
            "object": updated_object,
        })

    def delete(self, request, element_code, object_id):
        user = self.get_current_user(request)

        obj = find_mock_object(element_code, object_id, user)

        if obj is None:
            return Response(
                {"detail": "Mock object not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_delete(user, element_code, obj["owner_id"]):
            raise ForbiddenError("You do not have delete access to this object.")

        return Response({
            "detail": "Mock object deleted. It was not stored in DB anyway.",
            "object": obj,
        })
