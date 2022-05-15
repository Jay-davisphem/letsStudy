from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm


def home(request):
    q = request.GET.get("q")
    q = q if q else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(description__icontains=q)
        | Q(host__username=q)
    )

    topics = Topic.objects.all()
    chats = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "rooms_count": rooms.count(),
        "chats": chats,
    }
    return render(request, "main/home.html", context)


def room(request, pk):
    room = Room.objects.get(pk=pk)
    chats = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)
    context = {"room": room, "chats": chats, "participants": participants}
    return render(request, "main/room.html", context)


@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {"form": form}
    return render(request, "main/room_form.html", context)


@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You don't have the permission to do this! ")
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {"form": form}
    return render(request, "main/room_form.html", context)


@login_required(login_url="/login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    context = {"room": room}

    if request.user != room.host:
        return HttpResponse("You don't have the permission to do this! ")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "main/delete.html", context)


def login_view(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exists!")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username OR password is incorrect!")
    context = {"page": page}
    return render(request, "main/login_register.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def register_view(request):
    page = "register"
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occured during registration")
    context = {"page": page, "form": form}
    return render(request, "main/login_register.html", context)


def delete_message(request, pk):
    chat = Message.objects.get(id=pk)
    context = {"chat": chat}

    if request.user != chat.user:
        return HttpResponse("You don't have the permission to do this! ")

    if request.method == "POST":
        room_id = chat.room.id
        chat.delete()
        return redirect("room", pk=room_id)
    return render(request, "main/delete.html", context)


def user_profile(request, pk):
    user = User.objects.get(pk=pk)
    chats = user.message_set.all()
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    context = {"user": user, "rooms": rooms, "chats": chats, "topics": topics}
    return render(request, "main/profile.html", context)
