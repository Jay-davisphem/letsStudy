from django.urls import path, re_path
from django.contrib.auth import views as views1
from rest_framework.routers import DefaultRouter

from . import views

app_name = "rest_framework"

# User viewset router
router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="users")

urlpatterns = [
    path("", views.get_routes_basic, name="root-api"),
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
    path('user/<int:pk>/', views.UserViewSet.as_view({"get": 'retrieve'}), name='user-detail'),
]

urlpatterns += router.urls
