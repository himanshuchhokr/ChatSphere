from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """A chat room that any authenticated user can create and join."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_rooms")
    members = models.ManyToManyField(User, related_name="rooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Message(models.Model):
    """A single chat message persisted for history/replay when joining a room."""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
