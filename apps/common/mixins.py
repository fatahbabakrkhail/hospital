from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class SoftDeleteMixin(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Mixin to handle soft delete, list deleted records, restore, and prevent updates on deleted items."""

    def get_model_name(self):
        """Dynamically get the model name for responses."""
        if self.queryset and hasattr(self.queryset, "model"):
            return self.queryset.model.__name__
        return "UnknownModel"  # ✅ More informative fallback

    
    def is_deletion_action(self):
        """Check if the action is related to listing or restoring soft-deleted records."""
        return self.action in ["list_deleted", "restore"]

    def get_queryset(self):
        """Modify queryset to exclude soft-deleted items by default."""
        if self.is_deletion_action():  # ✅ Cleaner code
            return self.queryset.model.all_objects.all()
        return self.queryset.model.objects.all()
    
    def perform_destroy(self, instance):
        """Call `soft_delete()` method from `BaseModel` to handle soft delete."""
        instance.soft_delete()  # ✅ Now it uses BaseModel's method
        return Response(
            {"message": f"{self.get_model_name()} soft deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


    def _prevent_soft_deleted_update(self, instance):
        """Helper method to prevent updates on soft-deleted records."""
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
        return None  # ✅ Ensure function always returns something

    def update(self, request, *args, **kwargs):
        """Prevent updating soft-deleted records."""
        instance = self.get_object()
        response = self._prevent_soft_deleted_update(instance)
        if response:
            return response
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Prevent partially updating soft-deleted records."""
        instance = self.get_object()
        response = self._prevent_soft_deleted_update(instance)
        if response:
            return response
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
        """Restore a soft-deleted record using `restore()` method from `BaseModel`."""
        instance = self.get_queryset().filter(id=pk, deleted_at__isnull=False).first()
        if not instance:
            return Response({"error": f"{self.get_model_name()} not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)

        instance.restore()  # ✅ Now it uses BaseModel's method
        return Response({"message": f"{self.get_model_name()} restored successfully."})
