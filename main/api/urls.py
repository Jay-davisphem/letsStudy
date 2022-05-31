from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.get_routes_basic, name="root-api"),
    re_path(r"^rooms/((?P<pk>[0-9]*)/)?$", views.get_rooms, name="rooms-list"),
    # path("rooms/<str:pk>/messages/", views.get_message, name="room-messages"),
    path("messages/<str:pk>/", views.get_message, name="message"),
    path("topics/", views.TopicView.as_view(), name="topic-list"),
    path("topics/<str:pk>/", views.TopicView.as_view(), name="topic-detail"),
]
