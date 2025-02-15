from django.db import models
from django.contrib.auth import get_user_model
from hospital.middleware import get_current_user
from .managers import BaseManager
from django.utils import timezone

User = get_user_model()

class BaseModel(models.Model):
    """Abstract base model with soft delete support and tracking fields."""

    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when this %(class)s was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text="Timestamp when this %(class)s was last updated."
    )
    deleted_at = models.DateTimeField(
        blank=True, null=True, 
        help_text="Timestamp when this %(class)s was soft deleted. Null if active."
    )

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name="%(class)s_created",
        help_text="User who created this %(class)s."
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name="%(class)s_updated",
        help_text="User who last updated this %(class)s."
    )
    deleted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name="%(class)s_deleted",
        help_text="User who soft deleted this %(class)s. Null if not deleted."
    )

    objects = BaseManager()  # ✅ Use custom manager to exclude deleted records
    all_objects = models.Manager()  # ✅ Allows access to ALL records, including deleted

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Automatically set created_by and updated_by fields."""
        user = get_current_user()  # ✅ Get the current user dynamically

        if not self.pk and not self.created_by and user:
            self.created_by = user
        if user:  # ✅ Only update `updated_by` if a user exists
            self.updated_by = user

        super().save(*args, **kwargs)

    def soft_delete(self):
        """Perform a soft delete (works for API, Admin, and Scripts)."""
        if self.deleted_at:  # ✅ Prevent redundant soft deletes
            return
        
        user = get_current_user()  # ✅ Get the current user dynamically
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["deleted_at", "deleted_by"])  # ✅ Only update these fields

    def restore(self):
        """Restore a soft-deleted record."""
        if not self.deleted_at:  # ✅ Prevent redundant restores
            return
        
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["deleted_at", "deleted_by"])  # ✅ Only update these fields
