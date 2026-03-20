from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class SquadMember(models.Model):
    class Role(models.TextChoices):
        LEAD = "LEAD"
        TANK = "TANK"
        SUPP = "SUPP"
        RECON = "RECON"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="squad"
    )
    character_id = models.PositiveIntegerField()
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.RECON)
    tactical_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #para não add personagens duplicados
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "character_id"], name="uniq_user_character"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.character_id} ({self.role})"
