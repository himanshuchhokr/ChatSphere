from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Room, Message
from .serializers import RegisterSerializer, RoomSerializer, MessageSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/register/ -> create a new user account."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class RoomViewSet(viewsets.ModelViewSet):
    """
    List/create chat rooms. Any authenticated user can create a room and
    it's visible to everyone (public rooms, like a Slack workspace's #channels).
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        room.members.add(self.request.user)

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        """POST /api/rooms/<id>/join/ -> add current user as a member."""
        room = self.get_object()
        room.members.add(request.user)
        return Response({"status": "joined"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """GET /api/rooms/<id>/messages/ -> last 50 messages, oldest first."""
        room = self.get_object()
        qs = room.messages.select_related("sender").order_by("-created_at")[:50]
        serializer = MessageSerializer(reversed(list(qs)), many=True)
        return Response(serializer.data)
