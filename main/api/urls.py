from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_routes, name="root-api"),
    path("rooms", views.get_rooms, name="rooms-list"),
    path("rooms/<str:pk>", views.get_room, name="room-detail"),
]
