from rest_framework import serializers
from main.models import Room, User, Topic, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "name"]


class RoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, required=False)

    class Meta:
        model = Room
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    # user = UserSerializer()

    class Meta:
        model = Message
        fields = "__all__"
        depth = 1
