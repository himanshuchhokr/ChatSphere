import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles a single WebSocket connection for one chat room.
    URL: ws://.../ws/chat/<room_slug>/?token=<jwt_access_token>
    """

    async def connect(self):
        self.room_slug = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = f"chat_{self.room_slug}"
        user = self.scope["user"]

        if isinstance(user, AnonymousUser):
            await self.close(code=4001)  # unauthorized
            return

        room_exists = await self.room_exists(self.room_slug)
        if not room_exists:
            await self.close(code=4004)  # room not found
            return

        await self.add_user_to_room(self.room_slug, user)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{user.username} joined the room",
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            user = self.scope.get("user")
            if user and not isinstance(user, AnonymousUser):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "system_message", "message": f"{user.username} left the room"},
                )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("message", "").strip()
        if not content:
            return

        user = self.scope["user"]
        message = await self.save_message(self.room_slug, user, content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message["content"],
                "sender": message["sender"],
                "timestamp": message["timestamp"],
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": event["message"],
        }))

    @database_sync_to_async
    def room_exists(self, slug):
        from .models import Room
        return Room.objects.filter(slug=slug).exists()

    @database_sync_to_async
    def add_user_to_room(self, slug, user):
        from .models import Room
        room = Room.objects.get(slug=slug)
        room.members.add(user)

    @database_sync_to_async
    def save_message(self, slug, user, content):
        from .models import Room, Message
        room = Room.objects.get(slug=slug)
        msg = Message.objects.create(room=room, sender=user, content=content)
        return {
            "content": msg.content,
            "sender": user.username,
            "timestamp": msg.created_at.isoformat(),
        }
