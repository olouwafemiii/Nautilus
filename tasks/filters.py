from django_filters import  rest_framework as filters
from .models import Tasks
from django.db.models import Q

class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    title = filters.CharFilter(field_name='title')
    class Meta:
        model = Tasks
        fields = ["status", "title"]
        order_by = ["-updated_at"]

    def filter_by_search_param(self, queryset, name, value):
        return queryset.filter(
            Q(status__icontains=value) | Q(title__icontains=value)
        )
        
