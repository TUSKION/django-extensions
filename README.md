# Django Essential Extensions

A focused Django package providing essential extensions for image management and subdomain redirects with advanced admin interface and middleware support.

## Features

- **ImageExtension**: Generic image management with support for multiple image types, ordering, and featured images
- **SubdomainRedirect**: Flexible subdomain redirect system with support for different redirect types
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