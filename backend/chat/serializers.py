from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from .models import Room, Message


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class RoomSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ("id", "name", "slug", "created_by", "member_count", "created_at")
        read_only_fields = ("id", "slug", "created_by", "created_at")

    def get_member_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        name = validated_data["name"]
        slug = slugify(name)
        validated_data["slug"] = slug
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "room", "sender", "content", "created_at")
        read_only_fields = ("id", "sender", "created_at")
