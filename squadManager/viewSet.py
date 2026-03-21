import requests
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SquadMember
from .serializers import (
    RegisterUserSerializer,
    SquadMemberSerializer,
    LoginSerializer,
)
from .utils import enrich_squad_members


from rest_framework_simplejwt.tokens import RefreshToken


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class SquadMemberViewSet(viewsets.ModelViewSet):
    serializer_class = SquadMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SquadMember.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "This character is already in your squad."}
            )

    @action(detail=False, methods=["get"], url_path="enriched")
    def list_with_character_data(self, request):
        members = list(self.get_queryset())
        enriched_members = enrich_squad_members(members)

        payload = [
            {
                "id": enriched["member"].id,
                "character_id": enriched["member"].character_id,
                "role": enriched["member"].role,
                "tactical_note": enriched["member"].tactical_note,
                "created_at": enriched["member"].created_at,
                "character": enriched["character"],
            }
            for enriched in enriched_members
        ]
        return Response(payload, status=status.HTTP_200_OK)


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        login(request, user)
        
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)