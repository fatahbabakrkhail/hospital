from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from hospital.middleware import get_current_user  

class SoftDeleteMixin(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Mixin to handle soft delete, list deleted records, restore, and prevent updates on deleted items."""

    def get_model_name(self):
        """Dynamically get the model name for responses."""
        return self.queryset.model.__name__ if self.queryset and self.queryset.model else "Record"

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.deleted_at = timezone.now()
        instance.deleted_by = get_current_user()
        instance.save()
        return Response(
            {"message": f"{self.get_model_name()} soft deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    def get_queryset(self):
        """Modify queryset to exclude soft-deleted items by default."""
        if self.action in ["list_deleted", "restore"]:  # ✅ Show soft-deleted records only for these actions
            return self.queryset.model.all_objects.all()
        return self.queryset.model.objects.all()  # ✅ Default: Only non-deleted records

    def update(self, request, *args, **kwargs):
        """Prevent updating soft-deleted records and provide detailed error message."""
        instance = self.get_object()
        if instance.deleted_at:
            return Response(
                {
                    "error": f"Cannot update a soft deleted {self.get_model_name()}.",
                    "id": instance.id,
                    "deleted_at": instance.deleted_at.strftime("%Y-%m-%d %H:%M:%S"),  # ✅ Show deletion timestamp
                    "deleted_by": instance.deleted_by.id if instance.deleted_by else None  # ✅ Show who deleted it
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Prevent partially updating soft-deleted records."""
        instance = self.get_object()
        if instance.deleted_at:
            return Response(
                {
                    "error": f"Cannot update a soft deleted {self.get_model_name()}.",
                    "id": instance.id,
                    "deleted_at": instance.deleted_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "deleted_by": instance.deleted_by.id if instance.deleted_by else None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="soft_deleted/list")
    def list_deleted(self, request):
        """List only soft-deleted records."""
        deleted_items = self.get_queryset().filter(deleted_at__isnull=False)  # ✅ Only soft-deleted
        serializer = self.get_serializer(deleted_items, many=True)
        return Response({
            "model": self.get_model_name(),
            "count": len(deleted_items),
            "data": serializer.data
        })

    @action(detail=True, methods=["post"], url_path="soft_deleted/restore")
    def restore(self, request, pk=None):
        """Restore a soft-deleted record."""
        instance = self.get_queryset().filter(id=pk, deleted_at__isnull=False).first()
        if not instance:
            return Response({"error": f"{self.get_model_name()} not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)

        instance.deleted_at = None
        instance.deleted_by = None
        instance.save()
        return Response({"message": f"{self.get_model_name()} restored successfully."})
