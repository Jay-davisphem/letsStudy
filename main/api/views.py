from rest_framework.decorators import api_view
from rest_framework.response import Response
from main.models import Room, Message, Topic, User
from django.http import Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import (
    RoomSerializer,
    MessageSerializer,
    TopicSerializer,
    UserSerializer,
)


@api_view(["GET"])
def get_routes_basic(request):
    routes = ["GET /api", "GET /api/rooms", "GET /api/rooms/:id"]
    return Response(routes)


@api_view(["GET", "POST", "PUT", "DELETE"])
def get_rooms(request, pk=None):
    print(dir(request))
    if request.method == "GET":
        if pk:
            room = get_object_or_404(Room, pk=pk)
            serializer = RoomSerializer(room)
            return Response(serializer.data)

        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        data = request.data
        topic = data["topic"]
        try:
            if isinstance(topic, str):
                topic = Topic.objects.get_or_create(name=topic)
            else:
                raise ValueError("Topic should be instance of str")
        except ValueError:
            return Response(
                {"detail": f"Cannot create or get {topic}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        print(topic)
        data["topic"] = topic[0].id
        data["host"] = request.user.id
        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
@api_view(["GET"])
def get_room_messages(request, pk):
    messages = Message.objects.filter(room__id=pk)
    serializer = MessageSerializer(messages, many=True)
    print(dir(serializer))
    return Response(serializer.data)


@api_view(["GET"])
def get_message(request, pk):
    message = Message.objects.get(pk=pk)
    serializer = MessageSerializer(message)
    return Response(serializer.data)
"""


class MessageActionAPIView(
    generics.RetrieveAPIView, generics.DestroyAPIView, generics.CreateAPIView
):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

get_message = MessageActionAPIView.as_view()


class TopicView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Topic, pk=pk)

    def get(self, request, pk=None):
        if pk:
            topic = self.get_object(pk)
            serializer = TopicSerializer(topic)
            return Response(serializer.data)

        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            name = Topic.objects.filter(name=serializer.validated_data["name"])
            if name:
                return Response(
                    {"detail": f"topic '{request.data.get('name')}' already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            print(serializer.validated_data["name"], 11)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        topic = self.get_object(pk)
        serializer = TopicSerializer(topic, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        topic = self.get_object(pk)
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
