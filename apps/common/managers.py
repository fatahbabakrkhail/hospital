from django.db import models

class BaseManager(models.Manager):
    """Custom manager that excludes soft-deleted items by default."""

    def get_queryset(self):
        """Return only objects that are NOT soft deleted."""
        return super().get_queryset().filter(deleted_at__isnull=True)