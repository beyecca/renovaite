import uuid

from django.db import models


class MagicLinkToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
  editable=False)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "magic_link_tokens"

    # TODO: add a management command or periodic task to hard-purge tokens where
    # expires_at < now() - timedelta(days=7) to prevent unbounded table growth.

    def __str__(self) -> str:
        return f"MagicLinkToken({self.email})"
