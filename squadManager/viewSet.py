import requests
from django.db import IntegrityError
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SquadMember
from .serializers import (
    RegisterUserSerializer,
    SquadMemberSerializer,
)
from .utils import enrich_squad_members


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SquadMemberViewSet(viewsets.ModelViewSet):
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

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )