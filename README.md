# Django Essential Extensions

A focused Django package providing essential extensions for image management, subdomain redirects, and SEO optimization with advanced admin interface and middleware support.

## Features

- **ImageExtension**: Generic image management with support for multiple image types, ordering, and featured images
- **SubdomainRedirect**: Flexible subdomain redirect system with support for different redirect types
- **SEOMixin**: Mixin-based SEO system for easy meta tag management across any Django model
- **Advanced Admin Interface**: Enhanced Django admin with dynamic object selectors, image previews, and validation
- **Middleware Support**: Built-in middleware for automatic subdomain redirects and admin IP restrictions
- **Custom Widgets**: Specialized form widgets for better user experience

## Installation

```bash
pip install git+https://github.com/TUSKION/django-extensions
```

## Quick Start

1. Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'essential_extensions',
]
```

2. Add middleware to your `MIDDLEWARE`:

```python
MIDDLEWARE = [
    # ... other middleware
    'essential_extensions.middleware.SubdomainRedirectMiddleware',
    'essential_extensions.middleware.AdminIPRestrictionMiddleware',  # Optional
]
```

3. Run migrations:

```bash
python manage.py migrate
```

4. The admin interface is automatically registered, but you can customize it:

```python
# admin.py
from essential_extensions.admin import ImageExtensionAdmin, SubdomainRedirectAdmin
from essential_extensions.models import ImageExtension, SubdomainRedirect

# Customize admin if needed
admin.site.unregister(ImageExtension)
admin.site.register(ImageExtension, ImageExtensionAdmin)
```

## ImageExtension

The ImageExtension provides a generic way to attach images to any Django model:

```python
from essential_extensions.models import ImageExtension

# Create an image extension for a game
game = Game.objects.get(id=1)
image = ImageExtension.objects.create(
    content_object=game,
    image_type='screenshot',
    image='path/to/image.jpg',
    title='Game Screenshot',
    alt_text='Screenshot of the game',
    description='A beautiful screenshot showing gameplay',
    order=1,
    is_featured=True
)

# Query images for an object
game_images = ImageExtension.objects.filter(
    content_type=ContentType.objects.get_for_model(Game),
    object_id=game.id
).order_by('order')

# Get featured images
featured_images = ImageExtension.objects.filter(is_featured=True)
```

### Image Types

- `screenshot`: Game screenshots
- `banner`: Banner images  
- `icon`: Icon images
- `logo`: Logo images
- `custom`: Custom image types (use `custom_type` field)

### Model Fields

- `content_object`: Generic foreign key to any Django model
- `image_type`: Predefined image type or 'custom'
- `custom_type`: Custom type name when `image_type` is 'custom'
- `image`: ImageField for the actual image file
- `title`: Human-readable title
- `alt_text`: Alt text for accessibility
- `description`: Optional description
- `order`: Integer for ordering images
- `is_featured`: Boolean to mark featured images
- `created_at`/`updated_at`: Timestamps

## SubdomainRedirect

Manage subdomain redirects with different redirect types:

```python
from essential_extensions.models import SubdomainRedirect

# Full redirect to a specific path
redirect = SubdomainRedirect.objects.create(
    subdomain='blog',
    redirect_type='full',
    redirect_path='/blog/',
    is_active=True
)

# Path preserving redirect (keeps the same path on main domain)
redirect = SubdomainRedirect.objects.create(
    subdomain='shop',
    redirect_type='path_preserve',
    is_active=True
)

# Link to a specific object (if it has get_absolute_url)
game = Game.objects.get(id=1)
redirect = SubdomainRedirect.objects.create(
    subdomain='gamex',
    redirect_type='full',
    content_object=game,  # Will use game.get_absolute_url()
    is_active=True
)
```

### Redirect Types

- `full`: Redirect to a specific path (requires `redirect_path`)
- `path_preserve`: Keep the same path on main domain (no `redirect_path` needed)

### Model Fields

- `subdomain`: The subdomain to redirect (e.g., 'blog' for blog.example.com)
- `redirect_type`: Type of redirect ('full' or 'path_preserve')
- `redirect_path`: Target path for full redirects
- `content_object`: Optional generic foreign key to a Django object
- `is_active`: Whether the redirect is active
- `created_at`/`updated_at`: Timestamps

## Middleware

### SubdomainRedirectMiddleware

Automatically handles subdomain redirects based on the SubdomainRedirect model:

```python
MIDDLEWARE = [
    # ... other middleware
    'essential_extensions.middleware.SubdomainRedirectMiddleware',
]
```

**Features:**
- Automatically detects subdomains
- Supports both full and path-preserving redirects
- Uses object URLs when content_object is set
- Configurable main domain via `MAIN_DOMAIN` setting

**Settings:**
```python
# settings.py
MAIN_DOMAIN = 'example.com'  # Your main domain
```

### AdminIPRestrictionMiddleware

Restricts Django admin access to specific IP addresses:

```python
MIDDLEWARE = [
    # ... other middleware
    'essential_extensions.middleware.AdminIPRestrictionMiddleware',
]
```

**Settings:**
```python
# settings.py
ADMIN_IP_RESTRICTION_ENABLED = True  # Enable/disable restriction
ADMIN_ALLOWED_IPS = [
    '192.168.1.100',
    '10.0.0.50',
]
ADMIN_ALLOWED_NETWORKS = [
    '192.168.1.0/24',
    '10.0.0.0/8',
]
```

**Features:**
- Supports individual IPs and network ranges
- Handles Cloudflare and proxy headers
- Secure by default (blocks all if no IPs configured)
- Detailed logging for debugging

## Admin Interface

The package provides an enhanced Django admin interface with:

### Generic Object Selector
- Dynamic dropdown that populates based on selected content type
- AJAX-powered object loading
- Automatic object ID field management

### Image Preview Widget
- Real-time image previews in admin forms
- Hover overlays with actions
- Responsive design

### Subdomain Input Widget
- Client-side validation
- Real-time feedback
- Automatic formatting and cleanup

### Custom Actions
- Bulk enable/disable featured images
- Duplicate images
- Mass operations

## Custom Widgets

### DynamicJSONEditorWidget

A JSON editor with formatting and validation:

```python
from essential_extensions.widgets import DynamicJSONEditorWidget

class MyForm(forms.ModelForm):
    json_data = forms.JSONField(
        widget=DynamicJSONEditorWidget(
            schema={'type': 'object', 'properties': {...}},
            default_value={}
        )
    )
```

### ImagePreviewWidget

Shows image previews in forms:

```python
from essential_extensions.widgets import ImagePreviewWidget

class MyForm(forms.ModelForm):
    image = forms.ImageField(
        widget=ImagePreviewWidget(preview_size=(200, 150))
    )
```

### SubdomainInputWidget

Specialized input for subdomain fields:

```python
from essential_extensions.widgets import SubdomainInputWidget

class MyForm(forms.ModelForm):
    subdomain = forms.CharField(
        widget=SubdomainInputWidget()
    )
```

## Templates

### Image Extension

```html
{% load essential_extensions_tags %}

<!-- Get all images for an object -->
{% get_images_for_object game as images %}
{% for image in images %}
    <img src="{{ image.image.url }}" alt="{{ image.alt_text }}" title="{{ image.title }}">
{% endfor %}

<!-- Get featured images only -->
{% get_featured_images_for_object game as featured_images %}
{% for image in featured_images %}
    <img src="{{ image.image.url }}" alt="{{ image.alt_text }}" class="featured">
{% endfor %}

<!-- Get images by type -->
{% get_images_by_type game 'screenshot' as screenshots %}
{% for screenshot in screenshots %}
    <img src="{{ screenshot.image.url }}" alt="{{ screenshot.alt_text }}">
{% endfor %}
```

### Subdomain Redirect

The subdomain redirects are handled automatically by the middleware, but you can check redirects in templates:

```html
{% load essential_extensions_tags %}

{% get_subdomain_redirect request.get_host as redirect %}
{% if redirect %}
    <p>This subdomain redirects to: {{ redirect.get_redirect_url }}</p>
{% endif %}
```

## Configuration

### Basic Settings

```python
# settings.py

# Main domain for subdomain redirects
MAIN_DOMAIN = 'example.com'

# Admin IP restriction
ADMIN_IP_RESTRICTION_ENABLED = True
ADMIN_ALLOWED_IPS = ['127.0.0.1', '::1']
ADMIN_ALLOWED_NETWORKS = ['192.168.1.0/24']

# Image upload settings
ESSENTIAL_EXTENSIONS_CONFIG = {
    'IMAGE_UPLOAD_PATH': 'essential_extensions/images/',
    'ALLOWED_IMAGE_TYPES': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'MAX_IMAGE_SIZE': 10 * 1024 * 1024,  # 10MB
}
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=essential_extensions
```

### Code Quality

```bash
# Format code
black essential_extensions/

# Lint code
flake8 essential_extensions/

# Type checking
mypy essential_extensions/
```

### Building

```bash
# Build package
python -m build

# Upload to PyPI (if you have access)
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [GitHub Wiki](https://github.com/TUSKION/django-extensions/wiki)
- **Issues**: [GitHub Issues](https://github.com/TUSKION/django-extensions/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TUSKION/django-extensions/discussions)

## SEOMixin

The SEOMixin provides a flexible, mixin-based system for managing SEO metadata across Django models. It supports multiple data sources, fallback mechanisms, and template tags for easy integration.

### Adding SEO to a Model

```python
from essential_extensions.mixins import SEOMixin

class GameProject(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    description = models.TextField()
    summary = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Define SEO field mapping
    _seo = {
        'title': 'title',
        'description': 'summary',  # Use summary field for description
        'keywords': ['title', 'description'],  # Generate keywords from these fields
        'image': 'hero_image',
        'author': 'GhostJam Team',  # Static value
        'robots': 'index, follow',
        'keyword_categories': 'categories',  # Dynamic keywords from categories
    }
    
    def get_absolute_url(self):
        return reverse('game_detail', args=[self.slug])
```

### SEO Methods

The mixin provides several methods for accessing SEO data:

```python
game = GameProject.objects.get(title='Amazing Game')

# Get SEO values
title = game.get_seo_title()
description = game.get_seo_description()
keywords = game.get_seo_keywords()
image = game.get_seo_image()
author = game.get_seo_author()
robots = game.get_seo_robots()
canonical_url = game.get_seo_canonical_url()

# Get any SEO value with fallbacks
custom_value = game.get_seo_value('custom_field', 'default_value')
```

### SEO Field Mapping

The `_seo` class attribute maps SEO properties to model fields or static values:

```python
class BlogPost(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    content = models.TextField()
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    
    _seo = {
        # Direct field mapping
        'title': 'title',
        'description': 'content',
        
        # Static values
        'author': 'GhostJam Team',
        'robots': 'index, follow',
        
        # Dynamic keyword generation
        'keyword_categories': 'categories',  # Uses category names
        'keyword_tags': 'tags',  # Uses tag names
        
        # Custom field with fallback
        'image': 'featured_image',
    }
```

### Data Source Priority

The mixin uses a priority system for SEO values:

1. **extra_data JSON field** - Highest priority for overrides
2. **_seo mapping** - Field mapping or static values
3. **Settings defaults** - Fallback to `SEO_DEFAULTS` setting
4. **Empty string** - Final fallback

```python
# Priority for description:
# 1. extra_data.get('description') - if exists
# 2. self.summary - if exists and not empty (from _seo mapping)
# 3. settings.SEO_DEFAULTS.get('description') - if exists
# 4. '' (empty string) - final fallback
```

### Dynamic Keyword Generation

The system can automatically generate keywords from model fields:

```python
class GameProject(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    
    _seo = {
        'keyword_categories': 'categories',  # Uses category.title
        'keyword_tags': 'tags',  # Uses tag.name
        'keyword_title': 'title',  # Uses title field
    }

# This will generate keywords from:
# - Category titles
# - Tag names  
# - Game title
# - Plus any manually set keywords
```

### Template Tags

#### Loading the Tags

```django
{% load seo_tags %}
```

#### Rendering Meta Tags

```django
<!-- Using an object with SEO methods -->
{% render_meta game %}

<!-- Using a meta dictionary -->
{% render_meta meta %}

<!-- With custom overrides -->
{% render_meta game title="Custom Title" description="Custom Description" %}
```

#### Meta Tag Template

The `render_meta` tag uses the `seo/meta_tags.html` template:

```django
<!-- seo/meta_tags.html -->
{% if title %}
    <title>{{ title }}</title>
    <meta property="og:title" content="{{ title }}">
    <meta name="twitter:title" content="{{ title }}">
{% endif %}

{% if description %}
    <meta name="description" content="{{ description }}">
    <meta property="og:description" content="{{ description }}">
    <meta name="twitter:description" content="{{ description }}">
{% endif %}

{% if keywords %}
    <meta name="keywords" content="{{ keywords|join:', ' }}">
{% endif %}

{% if image %}
    <meta property="og:image" content="{{ image }}">
    <meta name="twitter:image" content="{{ image }}">
{% endif %}

{% if author %}
    <meta name="author" content="{{ author }}">
    <meta property="article:author" content="{{ author }}">
{% endif %}

{% if robots %}
    <meta name="robots" content="{{ robots }}">
{% endif %}

{% if canonical_url %}
    <link rel="canonical" href="{{ canonical_url }}">
{% endif %}
```

### Complete Example

#### Model Setup

```python
from essential_extensions.mixins import SEOMixin

class GameProject(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    hero_image = models.ImageField(upload_to='games/')
    categories = models.ManyToManyField(Category)
    extra_data = models.JSONField(default=dict, blank=True)
    
    _seo = {
        'title': 'title',
        'description': 'summary',
        'image': 'hero_image',
        'author': 'GhostJam Team',
        'robots': 'index, follow',
        'keyword_categories': 'categories',
    }
    
    def get_absolute_url(self):
        return reverse('game_detail', args=[self.slug])
```

#### View Implementation

```python
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

def game_detail(request: HttpRequest, slug: str):
    game = get_object_or_404(GameProject, slug=slug)
    
    # Create meta object for template
    meta = {
        'title': game.get_seo_title(),
        'description': game.get_seo_description(),
        'keywords': game.get_seo_keywords(),
        'image': game.get_seo_image(),
        'author': game.get_seo_author(),
        'robots': game.get_seo_robots(),
        'canonical_url': request.build_absolute_uri(game.get_absolute_url()),
    }
    
    return render(request, 'games/detail.html', {
        'game': game,
        'meta': meta
    })
```

#### Template Usage

```django
{% extends "base.html" %}
{% load seo_tags %}

{% block head %}
    {% render_meta meta %}
{% endblock %}

{% block content %}
    <h1>{{ game.title }}</h1>
    <p>{{ game.summary }}</p>
    <!-- Rest of your content -->
{% endblock %}
```

### Settings Configuration

#### SEO Defaults

```python
# settings.py

SEO_DEFAULTS = {
    'description': 'GhostJam - Indie Game Development Community',
    'keywords': ['indie games', 'game development', 'game jam'],
    'author': 'GhostJam Team',
    'robots': 'index, follow',
    'image': '/static/images/default-og-image.jpg',
}
```

#### Custom Settings

```python
# settings.py

# Custom SEO settings
SEO_DEFAULT_TITLE_SUFFIX = ' - GhostJam'
SEO_MAX_DESCRIPTION_LENGTH = 160
SEO_MAX_KEYWORDS = 10
```

### Best Practices

#### Model Configuration

1. **Use descriptive field mapping**: Map SEO fields to appropriate model fields
2. **Provide fallbacks**: Always have sensible defaults
3. **Use static values**: For consistent values like author or robots
4. **Leverage dynamic keywords**: Automatically generate keywords from related fields

#### Template Usage

1. **Use the meta object**: Pass a meta object to templates for consistency
2. **Provide overrides**: Allow custom meta tags when needed
3. **Check for existence**: Always verify meta data exists before using
4. **Use canonical URLs**: Always provide canonical URLs for SEO

#### Data Management

1. **Keep extra_data clean**: Use extra_data for overrides, not primary data
2. **Update regularly**: Keep SEO data current with content changes
3. **Test meta tags**: Verify meta tags render correctly
4. **Monitor performance**: Ensure SEO methods don't impact performance

### Troubleshooting

#### Common Issues

1. **Meta tags not showing**: Check if the object has SEO methods
2. **Wrong values**: Verify the data source priority chain
3. **Performance issues**: Ensure SEO methods are efficient
4. **Missing defaults**: Check if settings.SEO_DEFAULTS is configured

#### Debug Tips

```python
# Check SEO values for an object
game = GameProject.objects.get(title='Amazing Game')

print(f"Title: {game.get_seo_title()}")
print(f"Description: {game.get_seo_description()}")
print(f"Keywords: {game.get_seo_keywords()}")
print(f"Image: {game.get_seo_image()}")

# Check extra_data
print(f"Extra data: {game.extra_data}")

# Check _seo mapping
print(f"SEO mapping: {game._seo}")
```

#### Template Debugging

```django
{% load seo_tags %}

<!-- Debug meta object -->
{% if meta %}
    <p>Meta object exists</p>
    <p>Title: {{ meta.title }}</p>
    <p>Description: {{ meta.description }}</p>
{% else %}
    <p>No meta object</p>
{% endif %}

<!-- Test render_meta -->
{% render_meta meta %}
```