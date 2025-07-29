from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import path
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from django.core.exceptions import ValidationError
import logging

from .models.ImageExtension import ImageExtension
from .models.SubdomainRedirect import SubdomainRedirect
from .widgets import DynamicJSONEditorWidget


class GenericObjectSelectorForm(forms.ModelForm):
    """Base form for models that use generic foreign keys with object selector"""
    
    object_selector = forms.CharField(
        widget=forms.Select(choices=[('', 'First select a content type above')]),
        required=False,
        help_text='Select the specific object to attach this to'
    )
    
    object_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        help_text='This field is automatically populated when you select an object above'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add JavaScript fallback text
        self.fields['object_selector'].help_text = '''
        Select the specific object to attach this to. 
        <br><small><strong>Note:</strong> Make sure to select an object from this dropdown. 
        If the dropdown doesn't populate, try refreshing the page.</small>
        '''
        
        # If editing existing instance, populate the selector
        if self.instance and self.instance.pk and hasattr(self.instance, 'content_object') and self.instance.content_object:
            content_obj = self.instance.content_object
            display_name = self._get_object_display_name(content_obj)
            
            self.fields['object_selector'].widget = forms.Select(choices=[
                (self.instance.object_id, display_name)
            ])
            self.fields['object_selector'].initial = self.instance.object_id
    
    def _get_object_display_name(self, obj):
        """Get display name for an object"""
        if hasattr(obj, 'title'):
            return obj.title
        elif hasattr(obj, 'name'):
            return obj.name
        else:
            return str(obj)
    
    def clean(self):
        cleaned_data = super().clean()
        object_selector = cleaned_data.get('object_selector')
        content_type = cleaned_data.get('content_type')
        object_id = cleaned_data.get('object_id')
        
        # Ensure we have content_type
        if not content_type:
            raise ValidationError("Please select a content type.")
        
        # Try to get object_id from selector first, then from direct field
        selected_id = None
        
        if object_selector and object_selector.strip():
            try:
                selected_id = int(object_selector)
            except (ValueError, TypeError):
                raise ValidationError("Invalid object selection.")
        elif object_id:
            selected_id = object_id
        
        if not selected_id:
            raise ValidationError("Please select an object to attach this to.")
        
        # Validate that the object exists for this content type
        model_class = content_type.model_class()
        if not model_class.objects.filter(pk=selected_id).exists():
            raise ValidationError("Selected object does not exist.")
        
        # Ensure object_id is set
        cleaned_data['object_id'] = selected_id
        return cleaned_data
    
    def save(self, commit=True):
        """Override save to ensure object_id is set"""
        instance = super().save(commit=False)
        
        # Double-check that object_id is set
        if not instance.object_id and self.cleaned_data.get('object_selector'):
            try:
                instance.object_id = int(self.cleaned_data['object_selector'])
            except (ValueError, TypeError):
                pass
        
        if commit:
            instance.save()
        return instance


class GenericObjectSelectorAdmin(admin.ModelAdmin):
    """Base admin for models that use generic foreign keys with object selector"""
    
    class Media:
        js = ('admin/js/generic_object_selector.js',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-objects/', self.admin_site.admin_view(self.get_objects_ajax), 
                 name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_get_objects'),
        ]
        return custom_urls + urls
    
    def get_objects_ajax(self, request):
        """AJAX endpoint to get objects for a content type"""
        content_type_id = request.GET.get('content_type')
        
        if not content_type_id:
            return JsonResponse({'objects': []})
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model_class = content_type.model_class()
            
            objects = []
            for obj in model_class.objects.all():
                # Get display name
                if hasattr(obj, 'title'):
                    name = obj.title
                elif hasattr(obj, 'name'):
                    name = obj.name
                else:
                    name = str(obj)
                
                objects.append({
                    'id': obj.pk,
                    'name': name
                })
            
            return JsonResponse({'objects': objects})
        
        except (ContentType.DoesNotExist, AttributeError):
            return JsonResponse({'objects': []})


class ImageExtensionInline(GenericTabularInline):
    model = ImageExtension
    extra = 1
    fields = ('image_type', 'custom_type', 'image', 'title', 'order', 'is_featured', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 60px; max-width: 100px; border-radius: 4px;" />')
        return 'No image'
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


class ImageExtensionForm(GenericObjectSelectorForm):
    class Meta:
        model = ImageExtension
        fields = ['content_type', 'object_id', 'image_type', 'custom_type', 'image', 'title', 'alt_text', 'description', 'order', 'is_featured']


class ImageExtensionAdmin(GenericObjectSelectorAdmin):
    form = ImageExtensionForm
    list_display = ('content_object', 'image_type', 'custom_type', 'title', 'is_featured', 'created_at')
    list_filter = ('image_type', 'is_featured', 'content_type')
    search_fields = ('title', 'custom_type', 'alt_text')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    actions = ['enable_featured', 'disable_featured', 'duplicate_selected']
    
    fieldsets = (
        ('Attach to Object', {
            'fields': ('content_type', 'object_selector', 'object_id'),
            'description': 'Select the type of object, then choose the specific object from the dropdown.'
        }),
        ('Image Details', {
            'fields': ('image_type', 'custom_type', 'image', 'image_preview')
        }),
        ('Optional Info', {
            'fields': ('title', 'alt_text', 'description', 'order', 'is_featured'),
            'classes': ('collapse',)
        }),
    )
 
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />')
        return 'No image'
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'
    
    def enable_featured(self, request, queryset):
        """Mark selected images as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} image(s) have been marked as featured.')
    enable_featured.short_description = "Mark selected images as featured"
    
    def disable_featured(self, request, queryset):
        """Remove featured status from selected images"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} image(s) have been unmarked as featured.')
    disable_featured.short_description = "Remove featured status from selected images"
    
    def duplicate_selected(self, request, queryset):
        """Duplicate selected images"""
        duplicated_count = 0
        for obj in queryset:
            # Create a copy with a new ID
            obj.pk = None
            obj.title = f"{obj.title} (Copy)" if obj.title else f"{obj.get_image_type_display()} (Copy)"
            obj.is_featured = False  # Start as not featured
            obj.save()
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} image(s) have been duplicated.')
    duplicate_selected.short_description = "Duplicate selected images"


class SubdomainRedirectForm(GenericObjectSelectorForm):
    class Meta:
        model = SubdomainRedirect
        fields = ['subdomain', 'is_active', 'redirect_type', 'redirect_path', 'content_type', 'object_id']


class SubdomainRedirectAdmin(GenericObjectSelectorAdmin):
    form = SubdomainRedirectForm
    list_display = ('subdomain', 'redirect_type', 'redirect_path', 'is_active', 'content_object', 'created_at')
    list_filter = ('is_active', 'redirect_type', 'content_type')
    search_fields = ('subdomain', 'redirect_path')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Subdomain', {
            'fields': ('subdomain', 'is_active'),
        }),
        ('Redirect Target', {
            'fields': ('redirect_type', 'redirect_path'),
        }),
        ('Attach to Object (optional)', {
            'fields': ('content_type', 'object_selector', 'object_id'),
            'description': 'Optionally link this redirect to a specific object.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(ImageExtension, ImageExtensionAdmin)
admin.site.register(SubdomainRedirect, SubdomainRedirectAdmin)