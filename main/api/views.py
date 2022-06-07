from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from rest_framework.response import Response
from main.models import Room, Message, Topic, User
from django.http import Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework import generics
from .serializers import (
    RoomSerializer,
    MessageSerializer,
    TopicSerializer,
    UserSerializer,
)
from rest_framework import viewsets

from ..permissions import IsOwner, ReadOnly

from .. import client

# APIView and functional based view doesn't support default pagination
paginator = PageNumberPagination()
paginator.page_size = 5


@api_view(["GET"])
def get_routes_basic(request):
    routes = ["GET /api", "GET /api/rooms", "GET /api/rooms/:id"]
    return Response(routes)


@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def get_rooms(request, pk=None):
    if request.method == "GET":
        if pk:
            room = get_object_or_404(Room, pk=pk)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        query = request.GET.get("q")
        if query:
            results = client.perform_search(query, "room")
            return Response(results)
        rooms = Room.objects.all()
        page = paginator.paginate_queryset(rooms, request)
        serializer = RoomSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif request.method == "POST":
        data = request.data
        topic = data.get("topic")
        name = data.get("name")
        try:
            if topic and name:
                topic = Topic.objects.get_or_create(name=topic)
            else:
                raise ValueError("Topic or name cannot be empty!")
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["topic"] = topic[0].id
        data["name"] = name
        serializer = RoomSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(host=request.user)
            id = serializer.data["id"]
            Room.objects.get(pk=id).participants.add(request.user)
            data = serializer.data
            participants = Room.objects.get(pk=id).participants
            data["participants"].append(request.user.id)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        room = get_object_or_404(Room, pk=pk)
        if room.host == request.user:
            serializer = RoomSerializer(
                room, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(request=request)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "No authorization."}, status=status.HTTP_403_FORBIDDEN
        )
    elif request.method == "DELETE":
        room = get_object_or_404(Room, pk=pk)
        if room.host == request.user:
            room.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "No authorization."}, status=status.HTTP_403_FORBIDDEN
        )


class MessageActionAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsOwner]


get_message = MessageActionAPIView.as_view()


class CreateListRoomMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        # request.POST contains form-data
        # request.data contains form-data, json, multipath
        # request.GET contains query-params same as request.query_params
        # request.FILES
        room = get_object_or_404(Room, pk=pk)

        try:
            if not request.data.get("body"):
                raise Exception("Body cannot be empty!")
            message = Message.objects.create(
                room=room, user=request.user, body=request.data.get("body")
            )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        room.participants.add(request.user)
        return Response(
            {"details": "Created successfully"}, status=status.HTTP_201_CREATED
        )

    def get(self, request, pk=None):
        query = request.GET.get("q")
        if query:
            results = client.perform_search(query, "message")
            return Response(results)
        messages = Message.objects.filter(room__id=pk)
        page = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class TopicView(APIView):
    permission_classes = [IsAuthenticated]

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
        if not request.user.has_perm("main.change_topic"):
            return Response(
                {"details": "You don't have permission to do this!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        topic = self.get_object(pk)
        serializer = TopicSerializer(topic, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.has_perm("main.delete_topic"):
            return Response(
                {"details": "You don't have permission to do this!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        topic = self.get_object(pk)
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# User CRUD operations and probably algolia search capabilities on the api
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"  # default

    def get_permissions(self):
        if self.action == "create" and self.request.user.is_authenticated:
            return [
                ReadOnly(),
            ]
        if self.action == "create" and not self.request.user.is_authenticated:
            return [AllowAny()]
        if (
            self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            return [IsOwner()]
        return super().get_permissions()
