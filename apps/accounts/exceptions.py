from rest_framework.exceptions import APIException


class UnauthorizedError(APIException):
    status_code = 401
    default_detail = "Authentication credentials were not provided or invalid."
    default_code = "unauthorized"


class ForbiddenError(APIException):
    status_code = 403
    default_detail = "You do not have permission to perform this action."
    default_code = "forbidden"