from django.db import models
from apps.common.models import BaseModel

class Department(BaseModel):
    """
    Represents a hospital department.

    This model stores information about different hospital departments, 
    including their name, description, status (active/inactive), 
    and timestamps for creation, updates, and deletion. 

    It also tracks the user responsible for creating, updating, and 
    deleting each department record.
    """

    name = models.CharField(
        max_length=64, 
        unique=True,
        help_text="Unique name of the department (e.g., Cardiology, Neurology)."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Optional detailed description of the department."
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Indicates if the department is active."
    )
    class Meta:
        db_table = "department"  # ✅ Matches the database table name

    def __str__(self):
        """Returns the department name as its string representation."""
        return self.name
