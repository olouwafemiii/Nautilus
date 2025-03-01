from rest_framework import serializers
from .models import Tasks
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "status",
            "owner",
        ]

        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at'
        ]

    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("The due date can't be in the past")
        return value
