from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils.module_loading import import_string


def _default_dynamic_upload_path(instance, filename):
    """Generate upload path based on content type and object"""
    content_type = instance.content_type.model
    return f'extensions/{content_type}/{instance.object_id}/{filename}'

def dynamic_upload_path(instance, filename):
    """Wrapper to allow upload path to be defined via settings. Defaults to _default_dynamic_upload_path."""
    upload_path_func = getattr(settings, 'IMAGE_EXTENSION_UPLOAD_PATH', None)
    if upload_path_func:
        func = import_string(upload_path_func)
        return func(instance, filename)
    return _default_dynamic_upload_path(instance, filename)


class ImageExtensionManager(models.Manager):
    def prefetch_for_objects(self, objects):
        """
        Prefetch all images for a list of objects and return a cache.
        This eliminates N+1 queries when accessing images in templates.
        
        Usage:
            images_cache = ImageExtension.objects.prefetch_for_objects([game1, game2, blog_post1])
            # Then in template: {% get_images game 'hero' images_cache=images_cache %}
            # Or: {% get_image game 'hero' images_cache=images_cache %}
        """
        if not objects:
            return {}
        
        # Group objects by their content type
        content_types = {}
        for obj in objects:
            content_type = ContentType.objects.get_for_model(obj)
            if content_type not in content_types:
                content_types[content_type] = []
            content_types[content_type].append(obj.id)
        
        # Fetch all images for all content types in one query
        all_images = self.filter(
            content_type__in=content_types.keys()
        ).filter(
            object_id__in=[obj.id for obj in objects]
        ).order_by('object_id', 'image_type', 'order', '-is_featured')
        
        # Create a cache organized by object_id
        images_cache = {}
        for image in all_images:
            if image.object_id not in images_cache:
                images_cache[image.object_id] = []
            images_cache[image.object_id].append(image)
        
        return images_cache
    
    def prefetch_for_model_type(self, objects, model_class):
        """
        Prefetch images for objects of a specific model type.
        More efficient when you only need images for one model type.
        
        Usage:
            game_images = ImageExtension.objects.prefetch_for_model_type(games, GameProject)
            blog_images = ImageExtension.objects.prefetch_for_model_type(blog_posts, BlogPost)
            # Then in template: {% get_images game 'hero' images_cache=game_images %}
        """
        if not objects:
            return {}
        
        content_type = ContentType.objects.get_for_model(model_class)
        object_ids = [obj.id for obj in objects]
        
        all_images = self.filter(
            content_type=content_type,
            object_id__in=object_ids
        ).order_by('object_id', 'image_type', 'order', '-is_featured')
        
        images_cache = {}
        for image in all_images:
            if image.object_id not in images_cache:
                images_cache[image.object_id] = []
            images_cache[image.object_id].append(image)
        
        return images_cache


class ImageExtension(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('logo', 'Logo (Recommended: 512x512, PNG with transparency)'),
        ('icon', 'Icon (Recommended: 64x64 or 128x128, PNG)'),
        ('banner', 'Banner (Recommended: 1920x480, JPG/PNG)'),
        ('thumbnail', 'Thumbnail (Recommended: 600x900, JPG)'),
        ('hero', 'Hero Image (Recommended: 1920x1080, JPG)'),
        ('screenshot', 'Screenshot (Recommended: 1920x1080, JPG)'),
        ('gallery', 'Gallery Image (Any size, JPG/PNG)'),
        ('other', 'Other (Specify in custom type field)'),
    ]

    # Generic foreign key to attach to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Image details
    image_type = models.CharField(max_length=100, choices=IMAGE_TYPE_CHOICES, help_text='What type of image is this?')
    custom_type = models.CharField(max_length=50, blank=True, help_text='Custom image type if "Other" is selected above')
    image = models.ImageField(upload_to=dynamic_upload_path, help_text='The image file')
    
    # Metadata
    title = models.CharField(max_length=100, blank=True, help_text='Optional title/caption for the image')
    alt_text = models.CharField(max_length=200, blank=True, help_text='Alt text for accessibility (auto-generated if empty)')
    description = models.TextField(blank=True, help_text='Optional description of the image')
    
    # Organization
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower numbers shown first)')
    is_featured = models.BooleanField(default=False, help_text='Feature this image prominently')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ImageExtensionManager()

    class Meta:
        verbose_name = "Image Extension"
        verbose_name_plural = "Image Extensions"
        ordering = ['image_type', 'order', '-is_featured', 'id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['image_type']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        if self.title:
            image_desc = self.title
        elif self.image_type == 'other' and self.custom_type:
            image_desc = self.custom_type
        else:
            image_desc = self.get_image_type_display().split(' (')[0]  # Remove size recommendation from display
        return f"{self.content_object} - {image_desc}"
    
    def save(self, *args, **kwargs):
        # Auto-generate alt text if empty
        if not self.alt_text and self.title:
            self.alt_text = self.title
        elif not self.alt_text:
            self.alt_text = f"{self.get_image_type_display()} for {self.content_object}"
        super().save(*args, **kwargs)
    
    @property
    def url(self):
        """Convenience property to get image URL"""
        return self.image.url if self.image else None
