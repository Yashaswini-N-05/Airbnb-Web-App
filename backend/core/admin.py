from django.contrib import admin
from django.utils.html import format_html
from .models import Country, City


class BaseModelAdmin(admin.ModelAdmin):
    """Base admin class for models with timestamps"""
    readonly_fields = ['created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        # Add timestamps fieldset if not already present
        timestamp_fields = ['created_at', 'updated_at']
        has_timestamp_fieldset = any(
            any(field in fieldset[1]['fields'] for field in timestamp_fields)
            for fieldset in fieldsets
        )
        
        if not has_timestamp_fieldset:
            fieldsets.append((
                'Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }
            ))
        return fieldsets


class SoftDeleteAdminMixin:
    """Mixin to add soft delete functionality to admin"""
    
    def get_queryset(self, request):
        # Show all objects including soft-deleted ones in admin
        return self.model.all_objects.get_queryset()
    
    def delete_model(self, request, obj):
        # Soft delete single object
        obj.delete()
    
    def delete_queryset(self, request, queryset):
        # Soft delete multiple objects
        for obj in queryset:
            obj.delete()
    
    def deleted_status(self, obj):
        if obj.is_deleted:
            return format_html('<span style="color: red;">Deleted</span>')
        return format_html('<span style="color: green;">Active</span>')
    deleted_status.short_description = 'Status'
    
    def restore_objects(self, request, queryset):
        """Admin action to restore soft-deleted objects"""
        count = 0
        for obj in queryset.filter(is_deleted=True):
            obj.restore()
            count += 1
        self.message_user(request, f'{count} objects restored successfully.')
    restore_objects.short_description = "Restore selected objects"
    
    def hard_delete_objects(self, request, queryset):
        """Admin action to permanently delete objects"""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f'{count} objects permanently deleted.')
    hard_delete_objects.short_description = "Permanently delete selected objects"


class SoftDeleteModelAdmin(SoftDeleteAdminMixin, BaseModelAdmin):
    """Base admin class for soft delete models"""
    
    def get_list_filter(self, request):
        """Add is_deleted to list_filter if not already present"""
        list_filter = list(getattr(self, 'list_filter', []))
        if 'is_deleted' not in list_filter:
            list_filter.append('is_deleted')
        return list_filter
    
    def get_actions(self, request):
        """Add soft delete actions if not already present"""
        actions = super().get_actions(request)
        if 'restore_objects' not in actions:
            actions['restore_objects'] = (self.restore_objects, 'restore_objects', self.restore_objects.short_description)
        if 'hard_delete_objects' not in actions:
            actions['hard_delete_objects'] = (self.hard_delete_objects, 'hard_delete_objects', self.hard_delete_objects.short_description)
        return actions
    
    def get_readonly_fields(self, request, obj=None):
        """Add soft delete fields to readonly fields"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        soft_delete_fields = ['deleted_at']
        for field in soft_delete_fields:
            if field not in readonly_fields:
                readonly_fields.append(field)
        return readonly_fields
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        # Add soft delete fieldset if not already present
        soft_delete_fields = ['is_deleted', 'deleted_at']
        has_soft_delete_fieldset = any(
            any(field in fieldset[1]['fields'] for field in soft_delete_fields)
            for fieldset in fieldsets
        )
        
        if not has_soft_delete_fieldset:
            fieldsets.insert(-1, (
                'Soft Delete Info', {
                    'fields': ('is_deleted', 'deleted_at'),
                    'classes': ('collapse',)
                }
            ))
        return fieldsets


@admin.register(Country)
class CountryAdmin(SoftDeleteModelAdmin):
    list_display = ['name', 'code', 'currency', 'is_active', 'deleted_status', 'created_at']
    list_filter = ['is_active', 'currency', 'is_deleted']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'currency', 'phone_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(City)
class CityAdmin(SoftDeleteModelAdmin):
    list_display = ['name', 'country', 'is_popular', 'is_active', 'deleted_status', 'created_at']
    list_filter = ['country', 'is_popular', 'is_active', 'is_deleted']
    search_fields = ['name', 'country__name']
    ordering = ['country__name', 'name']
    raw_id_fields = ['country']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'country')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'timezone')
        }),
        ('Status', {
            'fields': ('is_popular', 'is_active')
        }),
    )
