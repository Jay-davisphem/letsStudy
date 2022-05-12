from django.shortcuts import render
from django.http import HttpResponse

rooms = [
    {"id": 1, "name": "Lets learn python"},
    {"id": 2, "name": "Design with me"},
    {"id": 3, "name": "Backend developer"},
]


def home(request):
    return render(request, "main/home.html", {"rooms": rooms})


def room(request, pk):
    return render(request, "main/room.html")
