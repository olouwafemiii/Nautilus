from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    )

    list_filter = (
        'is_staff',
        'is_active',
    )

    search_fields = ('email', 'first_name', 'last_name')


    fields = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )

    ordering = ('-date_joined',)


admin.site.register(User, UserAdmin)
