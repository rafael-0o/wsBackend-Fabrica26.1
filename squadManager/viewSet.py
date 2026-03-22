import requests
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse

from .models import SquadMember
from .serializers import (
    RegisterUserSerializer,
    SquadMemberSerializer,
    LoginSerializer,
    SquadMemberEnrichedSerializer,
    TokenResponseSerializer,
)
from .utils import enrich_squad_members


from rest_framework_simplejwt.tokens import RefreshToken


class IsOwner(permissions.BasePermission):
    """
    Custom permission to ensure that users can only access their own squad members.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


@extend_schema_view(
    list=extend_schema(summary="List squad members", tags=["Squad"]),
    retrieve=extend_schema(summary="View member details", tags=["Squad"]),
    create=extend_schema(summary="Recruit new member", tags=["Squad"]),
    update=extend_schema(summary="Update member (complete)", tags=["Squad"]),
    partial_update=extend_schema(summary="Update member (partial)", tags=["Squad"]),
    destroy=extend_schema(summary="Remove member from squad", tags=["Squad"]),
)
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

    @extend_schema(
        summary="List squad with extra character data",
        tags=["Squad"],
        responses={200: SquadMemberEnrichedSerializer(many=True)},
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

    @extend_schema(
        summary="Register new user",
        description="Creates an account and returns JWT tokens.",
        tags=["Authentication"],
        responses={201: TokenResponseSerializer},
        auth=[],
    )
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

    @extend_schema(
        summary="Login",
        description="Authenticates the user and returns JWT tokens.",
        tags=["Authentication"],
        responses={200: TokenResponseSerializer},
        auth=[],
    )
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

    @extend_schema(
        summary="Logout",
        description="Logs out the current user (session-based). For JWT, simply discard the token on the client side.",
        tags=["Authentication"],
        responses={204: OpenApiResponse(description="Logged out successfully")},
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)