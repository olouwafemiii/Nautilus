import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .constants import *

User = get_user_model()

# Create your models here.
class Tasks(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=255, 
        blank=False
    )
    description = models.TextField(
        blank=True
    )
    due_date = models.DateField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=TASKS_STATUS_CHOICES,
        default="pending"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='tasks',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
