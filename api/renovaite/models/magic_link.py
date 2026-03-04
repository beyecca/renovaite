import uuid

from django.db import models


class MagicLinkToken(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "magic_link_tokens"

    def __str__(self) -> str:
        return f"MagicLinkToken({self.email})"
