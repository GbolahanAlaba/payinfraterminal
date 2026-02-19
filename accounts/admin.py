from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, AccountType
from merchants.models import Merchant, KYCDocument


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('profile_id', 'created_at', 'updated_at')
    fields = (
        'account_type',
        'phone',
        'gender',
        'image',
        'bio',
        'address',
        'country',
        'state',
        'profile_id',
        'pin',
        'created_at',
        'updated_at',
    )


class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 1
    fields = ('document_type', 'document_file', 'verified', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


class MerchantInline(admin.StackedInline):
    model = Merchant
    extra = 0
    fields = (
        'merchant_id',
        'business_name',
        'business_email',
        'business_phone',
        'merchant_type',
        'website',
        'address',
        'country',
        'state',
        'is_verified',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('merchant_id', 'created_at', 'updated_at')
    inlines = [KYCDocumentInline]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline, MerchantInline]
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_admin',
        'is_staff',
        'is_active',
        'is_approved',
        'date_joined',
        'last_login',
    )
    list_filter = ('is_admin', 'is_staff', 'is_active', 'is_approved')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superuser', 'is_approved', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_admin', 'is_staff', 'is_active', 'is_approved')}
        ),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
