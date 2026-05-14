class CustomJWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.auth_user = None
        request.auth_session = None
        request.auth_error = None

        return self.get_response(request)