from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, HostVerification, UserActivity


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['bio', 'website', 'profile_public', 'show_reviews']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin with role support"""
    
    list_display = (
        'email', 'first_name', 'last_name', 'role', 
        'email_verified', 'is_verified_host', 'host_approval_status',
        'is_active', 'date_joined'
    )
    list_filter = (
        'role', 'email_verified', 'is_verified_host', 
        'host_approval_status', 'is_active', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'phone', 'date_of_birth',
                'country', 'city', 'avatar'
            )
        }),
        ('Role & Status', {
            'fields': (
                'role', 'is_verified_host', 'host_approval_status',
                'email_verified', 'email_verification_token'
            )
        }),
        ('Host Information', {
            'fields': ('business_name', 'business_license', 'tax_id'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_currency', 'preferred_language'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'role', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    actions = ['approve_hosts', 'reject_hosts', 'verify_emails']
    
    def approve_hosts(self, request, queryset):
        """Approve selected hosts"""
        updated = queryset.filter(role=User.HOST).update(
            host_approval_status='approved',
            is_verified_host=True
        )
        self.message_user(request, f'{updated} hosts were approved.')
    approve_hosts.short_description = "Approve selected hosts"
    
    def reject_hosts(self, request, queryset):
        """Reject selected hosts"""
        updated = queryset.filter(role=User.HOST).update(
            host_approval_status='rejected',
            is_verified_host=False
        )
        self.message_user(request, f'{updated} hosts were rejected.')
    reject_hosts.short_description = "Reject selected hosts"
    
    def verify_emails(self, request, queryset):
        """Verify emails for selected users"""
        updated = queryset.update(
            email_verified=True,
            email_verification_token=None
        )
        self.message_user(request, f'{updated} users email addresses were verified.')
    verify_emails.short_description = "Verify email addresses"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin"""
    
    list_display = (
        'user', 'get_user_role', 'profile_public', 
        'show_reviews', 'show_contact_info', 'created_at'
    )
    list_filter = (
        'profile_public', 'show_reviews', 'show_contact_info',
        'instant_booking', 'created_at'
    )
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('bio', 'website')
        }),
        ('Guest Preferences', {
            'fields': ('travel_preferences', 'loyalty_programs'),
            'classes': ('collapse',)
        }),
        ('Host Information', {
            'fields': ('hosting_experience', 'property_types', 'instant_booking'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('profile_public', 'show_reviews', 'show_contact_info')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_role(self, obj):
        return obj.user.get_role_display()
    get_user_role.short_description = 'Role'
    get_user_role.admin_order_field = 'user__role'


@admin.register(HostVerification)
class HostVerificationAdmin(admin.ModelAdmin):
    """Host verification admin"""
    
    list_display = (
        'user', 'identity_verified', 'address_verified', 
        'business_verified', 'verification_completion',
        'verified_by', 'verified_at'
    )
    list_filter = (
        'identity_verified', 'address_verified', 'business_verified',
        'verified_at', 'created_at'
    )
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'verification_completion')
    
    fieldsets = (
        ('Host', {
            'fields': ('user',)
        }),
        ('Documents', {
            'fields': (
                'identity_document', 'address_proof',
                'business_registration', 'insurance_certificate'
            )
        }),
        ('Verification Status', {
            'fields': (
                'identity_verified', 'address_verified', 'business_verified'
            )
        }),
        ('Admin Notes', {
            'fields': ('verification_notes', 'verified_by', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_completion(self, obj):
        percentage = obj.verification_completion_percentage()
        color = 'green' if percentage == 100 else 'orange' if percentage > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    verification_completion.short_description = 'Completion'
    
    actions = ['verify_identity', 'verify_address', 'verify_business']
    
    def verify_identity(self, request, queryset):
        updated = queryset.update(identity_verified=True)
        self.message_user(request, f'{updated} identity verifications were completed.')
    verify_identity.short_description = "Verify identity documents"
    
    def verify_address(self, request, queryset):
        updated = queryset.update(address_verified=True)
        self.message_user(request, f'{updated} address verifications were completed.')
    verify_address.short_description = "Verify address documents"
    
    def verify_business(self, request, queryset):
        updated = queryset.update(business_verified=True)
        self.message_user(request, f'{updated} business verifications were completed.')
    verify_business.short_description = "Verify business documents"


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """User activity admin"""
    
    list_display = (
        'user', 'activity_type', 'description', 
        'ip_address', 'created_at'
    )
    list_filter = ('activity_type', 'created_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'activity_type', 'description'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Activity', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Activities should be created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Activities should not be modified


# Customize admin site
admin.site.site_header = 'Trip Nest Administration'
admin.site.site_title = 'Trip Nest Admin'
admin.site.index_title = 'Welcome to Trip Nest Administration'
