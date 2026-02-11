from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = (
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_by',
        'date_joined',
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
    )
    search_fields = ('email',)

    # ⚠️ IMPORTANT : username supprimé
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Clés cryptographiques'), {'fields': ('public_key',)}),
        (_('Créé par'), {'fields': ('created_by',)}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
