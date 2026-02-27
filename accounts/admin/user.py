from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User
from accounts.admin.profile import ProfileInline
from merchants.admin import MerchantInline

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline, MerchantInline]
    list_display = (
        'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_approved',
        'date_joined', 'last_login',
    )
    list_filter = ('is_staff', 'is_active', 'is_approved')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_approved', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'is_approved')}
        ),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)