# ChatSphere 💬

A real-time chat application built with **Django Channels (WebSockets)** and **React**. Users can register, create/join public chat rooms, and exchange messages instantly — all messages persist to the database so history reloads on rejoin.

![Tech](https://img.shields.io/badge/Backend-Django%20Channels-092E20?logo=django)
![Tech](https://img.shields.io/badge/Realtime-WebSockets-black)
![Tech](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react)
![Tech](https://img.shields.io/badge/Auth-JWT-black)

## Features

- 🔐 JWT authentication (register, login, auto token refresh)
- ⚡ Real-time messaging over WebSockets (Django Channels + `AsyncWebsocketConsumer`)
- 🏠 Create and join public chat rooms
- 💾 Full message history persisted in the database, replayed on join
- 🟢 Live connection status indicator, join/leave system messages
- 🧪 Backend tests cover REST endpoints **and** the WebSocket flow itself (via `channels.testing.WebsocketCommunicator`)

## Tech Stack

| Layer     | Tech                                                        |
|-----------|--------------------------------------------------------------|
| Backend   | Python, Django, Django Channels, Django REST Framework, SimpleJWT |
| Real-time | WebSockets via Channels (in-memory layer for dev; swap to Redis for prod) |
| Frontend  | React, Vite, React Router, native WebSocket API              |
| Database  | SQLite (dev) — swap to PostgreSQL for production             |

## How real-time auth works

Browsers can't send custom headers during a WebSocket handshake, so the JWT access token is passed as a query parameter (`?token=...`) and validated by a custom `JWTAuthMiddleware` (see `backend/chat/middleware.py`) before the connection is accepted.

## Project Structure

```
chat-app/
├── backend/
│   ├── chat/                 # Models, consumers, routing, REST views, tests
│   │   ├── consumers.py       # WebSocket chat logic
│   │   ├── middleware.py      # JWT auth for WebSocket connections
│   │   └── routing.py         # WebSocket URL patterns
│   └── chatproject/           # Settings, ASGI/WSGI, root urls
└── frontend/
    └── src/
        ├── api/client.js      # REST + WebSocket client
        └── components/        # Login, Register, RoomList, ChatRoom
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```
API + WebSocket server runs at `http://localhost:8000` (Django's dev server handles ASGI automatically via `runserver` when Channels is installed).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
App runs at `http://localhost:5173`

## API Endpoints

| Method | Endpoint                     | Description                  |
|--------|-------------------------------|-------------------------------|
| POST   | `/api/register/`              | Create a new account          |
| POST   | `/api/token/`                  | Log in, get JWT tokens        |
| POST   | `/api/token/refresh/`          | Refresh access token          |
| GET/POST | `/api/rooms/`                | List / create chat rooms      |
| POST   | `/api/rooms/<id>/join/`        | Join a room                   |
| GET    | `/api/rooms/<id>/messages/`    | Last 50 messages in a room    |
| WS     | `/ws/chat/<room_slug>/?token=` | Real-time message stream      |

## Running Tests

```bash
cd backend
python manage.py test chat
```
This includes a live WebSocket test that connects, sends a message, and asserts it's broadcast back correctly.

## Roadmap / Ideas

- [ ] Typing indicators
- [ ] Private 1-on-1 DMs
- [ ] Online user list per room
- [ ] Redis channel layer + Docker Compose for production
- [ ] Deploy: backend on Render (with Redis), frontend on Vercel

## Author

Built by **Himanshu Chhokar** — [LinkedIn](#) · [GitHub](#) · [Portfolio](#)
