# Image Extension

The Image Extension provides a flexible, generic image management system that can be attached to any Django model. It supports multiple image types, optimized caching, and provides convenient template tags for easy integration.

## Features

- **Generic Attachment**: Attach images to any Django model
- **Multiple Image Types**: Hero, thumbnail, logo, banner, screenshot, gallery, etc.
- **Custom Types**: Support for custom image types via the "other" category
- **Optimized Caching**: Prefetch images to eliminate N+1 queries
- **Admin Interface**: Full admin interface with image previews
- **Bulk Actions**: Enable/disable featured status, duplicate images
- **Ordering**: Control display order and featured status
- **Metadata**: Title, alt text, and description support

## Models

### ImageExtension

The main model for storing image data.

```python
class ImageExtension(models.Model):
    # Generic foreign key to attach to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Image details
    image_type = models.CharField(max_length=100, choices=IMAGE_TYPE_CHOICES)
    custom_type = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to=dynamic_upload_path)
    
    # Metadata
    title = models.CharField(max_length=100, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Organization
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Image Types

Supported image types with recommended dimensions:

- **logo**: 512x512, PNG with transparency
- **icon**: 64x64 or 128x128, PNG
- **banner**: 1920x480, JPG/PNG
- **thumbnail**: 600x900, JPG
- **hero**: 1920x1080, JPG
- **screenshot**: 1920x1080, JPG
- **gallery**: Any size, JPG/PNG
- **other**: Custom type (specify in custom_type field)

## Template Tags

### Loading the Tags

```django
{% load image_tags %}
```

### Getting Multiple Images

```django
{% get_images object 'hero' as hero_images %}
{% get_images object 'gallery' as gallery_images %}
{% get_images object 'custom_type' as custom_images %}
```

**With caching (recommended for lists):**
```django
{% get_images game 'hero' images_cache=images_cache as hero_images %}
```

### Getting a Single Image

```django
{% get_image object 'hero' as hero_image %}
{% get_image object 'thumbnail' featured=True as featured_thumbnail %}
{% get_image object 'logo' featured=False as non_featured_logo %}
```

**With caching:**
```django
{% get_image game 'hero' images_cache=images_cache as hero_image %}
```

### Convenience Tags

```django
{% get_featured_image object 'hero' as featured_hero %}
{% get_any_image object 'thumbnail' as any_thumbnail %}
```

## Python Usage

### Basic Usage

```python
from extensions.models.ImageExtension import ImageExtension

# Get all hero images for a game
hero_images = ImageExtension.objects.filter(
    content_type=ContentType.objects.get_for_model(game),
    object_id=game.id,
    image_type='hero'
).order_by('order', '-is_featured')

# Get featured thumbnail
featured_thumbnail = ImageExtension.objects.filter(
    content_type=ContentType.objects.get_for_model(game),
    object_id=game.id,
    image_type='thumbnail',
    is_featured=True
).first()
```

### Optimized Caching

For lists of objects, use the prefetch methods to avoid N+1 queries:

```python
from extensions.models.ImageExtension import ImageExtension

# Prefetch images for multiple objects
games = GameProject.objects.all()
images_cache = ImageExtension.objects.prefetch_for_objects(games)

# Pass cache to template
context = {
    'games': games,
    'images_cache': images_cache
}
```

**For single model types (more efficient):**
```python
# More efficient when all objects are the same type
images_cache = ImageExtension.objects.prefetch_for_model_type(games, GameProject)
```

## Admin Interface

### ImageExtensionAdmin

The admin interface provides:

- **Generic Object Selector**: Dropdown to select the object to attach images to
- **Image Preview**: Thumbnail previews in the list view
- **Bulk Actions**: Enable/disable featured status, duplicate images
- **Organized Fieldsets**: Logical grouping of fields
- **Validation**: Ensures proper object selection

### Inline Usage

```python
from extensions.admin import ImageExtensionInline

class GameProjectAdmin(admin.ModelAdmin):
    inlines = [ImageExtensionInline]
```

## Settings

### Custom Upload Path

You can customize the upload path by setting `IMAGE_EXTENSION_UPLOAD_PATH` in your settings:

```python
# settings.py
IMAGE_EXTENSION_UPLOAD_PATH = 'path.to.custom.upload.function'
```

The function should accept `(instance, filename)` parameters and return the upload path.

## File Organization

Images are organized by content type and object ID:

```
extensions/
├── gameproject/
│   ├── 123/
│   │   ├── hero_image.jpg
│   │   ├── thumbnail.png
│   │   └── logo.png
│   └── 456/
│       ├── hero_image.jpg
│       └── gallery/
│           ├── screenshot1.jpg
│           └── screenshot2.jpg
└── blogpost/
    └── 789/
        ├── banner.jpg
        └── featured_image.png
```

## Best Practices

### Performance

1. **Use caching for lists**: Always use `prefetch_for_objects()` when displaying lists
2. **Optimize queries**: Use `prefetch_for_model_type()` for single model types
3. **Limit image sizes**: Use appropriate image dimensions for each type

### Organization

1. **Use consistent naming**: Follow the established image type conventions
2. **Set proper alt text**: Always provide meaningful alt text for accessibility
3. **Order images**: Use the order field to control display sequence
4. **Feature important images**: Use the featured flag for primary images

### Template Usage

1. **Check for existence**: Always check if images exist before displaying
2. **Provide fallbacks**: Have default images for when no images are available
3. **Use appropriate tags**: Choose the right template tag for your use case

```django
{% get_featured_image game 'hero' as hero_image %}
{% if hero_image %}
    <img src="{{ hero_image.image.url }}" alt="{{ hero_image.alt_text }}" class="hero-image">
{% else %}
    <img src="{% static 'images/default-hero.jpg' %}" alt="Default hero image" class="hero-image">
{% endif %}
```

## Examples

### Game Detail Page

```django
{% load image_tags %}

<div class="game-hero">
    {% get_featured_image game 'hero' as hero_image %}
    {% if hero_image %}
        <img src="{{ hero_image.image.url }}" alt="{{ hero_image.alt_text }}" class="hero-image">
    {% endif %}
</div>

<div class="game-info">
    <div class="game-logo">
        {% get_image game 'logo' as logo %}
        {% if logo %}
            <img src="{{ logo.image.url }}" alt="{{ logo.alt_text }}" class="logo">
        {% endif %}
    </div>
    
    <div class="game-screenshots">
        {% get_images game 'screenshot' as screenshots %}
        {% for screenshot in screenshots %}
            <img src="{{ screenshot.image.url }}" alt="{{ screenshot.alt_text }}" class="screenshot">
        {% endfor %}
    </div>
</div>
```

### Game List with Caching

```python
# views.py
def game_list(request):
    games = GameProject.objects.all()
    images_cache = ImageExtension.objects.prefetch_for_objects(games)
    
    return render(request, 'games/list.html', {
        'games': games,
        'images_cache': images_cache
    })
```

```django
<!-- games/list.html -->
{% load image_tags %}

{% for game in games %}
    <div class="game-card">
        {% get_image game 'thumbnail' images_cache=images_cache as thumbnail %}
        {% if thumbnail %}
            <img src="{{ thumbnail.image.url }}" alt="{{ thumbnail.alt_text }}" class="game-thumbnail">
        {% endif %}
        
        <h3>{{ game.title }}</h3>
    </div>
{% endfor %}
```

## Troubleshooting

### Common Issues

1. **Images not showing**: Check if the object has the correct content type and object ID
2. **Performance issues**: Ensure you're using the caching methods for lists
3. **Upload errors**: Verify the upload path is writable and the media settings are correct
4. **Admin selector not working**: Refresh the page if the dropdown doesn't populate

### Debug Tips

```python
# Check if images exist for an object
from extensions.models.ImageExtension import ImageExtension
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(game)
images = ImageExtension.objects.filter(
    content_type=content_type,
    object_id=game.id
)
print(f"Found {images.count()} images for {game}")
```

## API Reference

### ImageExtensionManager Methods

- `prefetch_for_objects(objects)`: Prefetch images for multiple objects
- `prefetch_for_model_type(objects, model_class)`: Prefetch images for specific model type

### Template Tags

- `get_images(obj, image_type, images_cache=None)`: Get multiple images
- `get_image(obj, image_type, featured=None, images_cache=None)`: Get single image
- `get_featured_image(obj, image_type, images_cache=None)`: Get featured image
- `get_any_image(obj, image_type, images_cache=None)`: Get any image

### Model Properties

- `url`: Convenience property to get image URL
- `get_display_name()`: Get display name for the image 