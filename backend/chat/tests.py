from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework.test import APITestCase
from rest_framework import status
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from chatproject.asgi import application
from .models import Room, Message


class AuthTests(APITestCase):
    def test_register_and_login(self):
        resp = self.client.post(reverse("register"), {
            "username": "himanshu",
            "email": "himanshu@example.com",
            "password": "StrongPass123!",
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(reverse("token_obtain_pair"), {
            "username": "himanshu",
            "password": "StrongPass123!",
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)


class RoomTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="himanshu", password="StrongPass123!")
        resp = self.client.post(reverse("token_obtain_pair"), {
            "username": "himanshu",
            "password": "StrongPass123!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_create_room(self):
        resp = self.client.post("/api/rooms/", {"name": "General"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["slug"], "general")
        room = Room.objects.get(slug="general")
        self.assertIn(self.user, room.members.all())

    def test_join_and_list_messages(self):
        room = Room.objects.create(name="Random", slug="random", created_by=self.user)
        Message.objects.create(room=room, sender=self.user, content="hey there")

        resp = self.client.post(f"/api/rooms/{room.id}/join/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(f"/api/rooms/{room.id}/messages/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["content"], "hey there")


class WebSocketChatTests(TransactionTestCase):
    """Verifies the real-time messaging flow end-to-end over a WebSocket."""

    async def _get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="StrongPass123!")
        self.room = Room.objects.create(name="Dev Talk", slug="dev-talk", created_by=self.user)

    async def test_connect_send_and_receive_message(self):
        token = await self._get_token(self.user)
        communicator = WebsocketCommunicator(application, f"/ws/chat/dev-talk/?token={token}")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # system "joined" broadcast
        join_event = await communicator.receive_json_from()
        self.assertEqual(join_event["type"], "system")

        await communicator.send_json_to({"message": "Hello from tests!"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello from tests!")
        self.assertEqual(response["sender"], "alice")

        await communicator.disconnect()

    async def test_unauthenticated_connection_rejected(self):
        communicator = WebsocketCommunicator(application, "/ws/chat/dev-talk/")
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
