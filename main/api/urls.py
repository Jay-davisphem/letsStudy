from django.urls import path, re_path
from django.contrib.auth import views as views1
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

app_name = "rest_framework"

users_list = views.UserViewSet.as_view(
    {
        "get": "list",
    }
)
users_detail = views.UserViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
# User viewset router

schema_view = get_schema_view(
    openapi.Info(
        title="LetsStudy API",
        default_version="v1",
        description="A platform where like minds learn and connect",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="davidoluwafemi178@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", views.get_routes_basic, name="root-api"),
    path("auth/", obtain_auth_token),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("sign-up/", views.UserViewSet.as_view({"post": "create"})),
    path(
        "login/",
        views1.LoginView.as_view(template_name="rest_framework/login.html"),
        name="login",
    ),
    path("logout/", views1.LogoutView.as_view(), name="logout"),
    re_path(r"^rooms/((?P<pk>[0-9]*)/)?$", views.get_rooms, name="rooms-list"),
    path(
        "rooms/<str:pk>/messages/",
        views.CreateListRoomMessageAPIView.as_view(),
        name="room-messages",
    ),
    path("messages/<str:pk>/", views.get_message, name="message"),
    path("topics/", views.TopicView.as_view(), name="topic-list"),
    path("topics/<str:pk>/", views.TopicView.as_view(), name="topic-detail"),
    path("users/", users_list, name="users-list"),
    path("users/<int:pk>/", users_detail, name="users-detail"),
]

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
