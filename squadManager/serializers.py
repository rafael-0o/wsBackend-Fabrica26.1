from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SquadMember


class SquadMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquadMember
        fields = ("id", "character_id", "role", "tactical_note", "created_at")
        read_only_fields = ("id", "created_at")


class SquadMemberEnrichedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    character_id = serializers.IntegerField()
    role = serializers.CharField()
    tactical_note = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    character = serializers.JSONField(allow_null=True)


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user_model = get_user_model()
        return user_model.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

