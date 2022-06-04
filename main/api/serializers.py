from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from main.models import Room, User, Topic, Message


class UserSerializer(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField(read_only=True)
    # url_v2 = serializers.SerializerMethodField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name="rest_framework:users-detail",
        lookup_field="pk",
    )

    class Meta:
        model = User
        fields = ["pk", "url", "username", "name"]

    def get_url(self, obj):
        return f"localhost:8000/api/users/{obj.pk}/"

    def get_url_v2(self, obj):
        request = self.context.get("request")  # self.request
        if request is None:
            return None
        return reverse(
            "rest_framework:users-detail",
            kwargs={"pk": obj.pk},
            request=request,
        )


class RoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, required=False, read_only=True)
    host = serializers.ReadOnlyField(source="host.id")

    class Meta:
        model = Room
        fields = "__all__"

    def get_url_v2(self, obj):
        request = self.context.get("request")  # self.request
        if request is None:
            return None
        return reverse(
            "rest_framework:users-detail",
            kwargs={"pk": obj.pk},
            request=request,
        )


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    # user = UserSerializer()

    class Meta:
        model = Message
        fields = "__all__"
