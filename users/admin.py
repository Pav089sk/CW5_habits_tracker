from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    filter_horizontal = ('groups',)
    ordering = ('email',)
    list_display = ('email', 'is_staff', 'is_active', 'telegram_chat_id')
    search_fields = ('email',)
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Права доступа', {'fields': ('is_active', 'groups', 'is_staff', 'is_superuser',  'telegram_chat_id')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )