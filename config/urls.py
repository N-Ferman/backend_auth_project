from django.urls import path

from apps.accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
)

from apps.access.views import (
    RoleListCreateView,
    RoleDetailView,
    BusinessElementListCreateView,
    AccessRuleListCreateView,
    AccessRuleDetailView,
    UserRoleListCreateView,
    UserRoleDetailView,
)


urlpatterns = [
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),

    path("api/me/", MeView.as_view()),

    path("api/admin/roles/", RoleListCreateView.as_view()),
    path("api/admin/roles/<int:role_id>/", RoleDetailView.as_view()),

    path("api/admin/elements/", BusinessElementListCreateView.as_view()),

    path("api/admin/rules/", AccessRuleListCreateView.as_view()),
    path("api/admin/rules/<int:rule_id>/", AccessRuleDetailView.as_view()),

    path("api/admin/user-roles/", UserRoleListCreateView.as_view()),
    path("api/admin/user-roles/<int:user_role_id>/", UserRoleDetailView.as_view()),
]