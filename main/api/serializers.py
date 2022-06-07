from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from main.models import Room, User, Topic, Message


class UserSerializer(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField(read_only=True)
    # url_v2 = serializers.SerializerMethodField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name="rest_framework:users-detail",
        lookup_field="pk",
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Enter your password",
        style={"input_type": "password", "placeholder": "Password"},
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Enter password again",
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = User
        fields = [
            "pk",
            "url",
            "username",
            "name",
            "email",
            "is_active",
            "is_staff",
            "password",
            "confirm_password",
        ]
        read_only_fields = ["is_active", "is_staff"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"write_only": True}}

    def create(self, validated_data):
        name = validated_data["name"]
        uname = validated_data["username"]
        password = validated_data["password"]
        email = validated_data["email"]
        c_pass = validated_data["confirm_password"]
        if password != c_pass:
            raise ValidationError("Password does not match")
        if name and uname and password and email:
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            return user
        raise ValidationError("Invalid data input")

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
