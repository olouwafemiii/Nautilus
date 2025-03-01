from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from .models import Tasks
from rest_framework.response import Response
from .filters import TaskFilter
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TaskSerializer
from .constants import *

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.filter(status=PENDING)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Tasks.objects.none()
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to access this resource.")
        return Tasks.objects.filter(owner=self.request.user)

    @swagger_auto_schema(operation_description="Create a task")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_description="Update a task")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_description="Partial Update of a task")
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != self.request.user:
            raise PermissionDenied("You can only update your tasks")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_description="Delete a task")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != self.request.user:
            raise PermissionDenied("You can only delete your tasks")
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="List tasks with filter options",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrer par statut (pending, in_progress, completed)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Rechercher par titre (partie ou totalité)",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        user_tasks = self.get_queryset()
        total_tasks = user_tasks.count()

        status_distribution = (
            user_tasks.values("status").annotate(count=Count("status")).order_by("status")
        )

        return Response({
            "total_tasks" : total_tasks,
            "status_distribution": status_distribution,
        })
