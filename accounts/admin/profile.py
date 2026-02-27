from django.contrib import admin
from accounts.models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('profile_id', 'created_at', 'updated_at')
    fields = (
        'account_type', 'phone', 'gender', 'image', 'bio',
        'address', 'country', 'state', 'profile_id', 'pin',
        'created_at', 'updated_at',
    )