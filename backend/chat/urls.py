from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import RegisterView, RoomViewSet

router = DefaultRouter()
router.register("rooms", RoomViewSet, basename="room")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("", include(router.urls)),
]
