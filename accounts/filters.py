from django_filters import  rest_framework as filters
from .models import User
from django.db.models import Q, F


class UserFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    search = filters.CharFilter(method="filter_by_search_param")
    order_by = filters.OrderingFilter(
        fields=("first_name", "last_name", "email", "date_joined"),
        field_labels={
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
            "date_joined": "Date joined",
        },
    )

    class Meta:
        model = User
        fields = ["start_date", "end_date", "search"]
        order_by = ["-updated_at"]

    def filter_by_search_param(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
        )
