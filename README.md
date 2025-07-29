# Django Essential Extensions

A focused Django package providing essential extensions for image management and subdomain redirects.

## Features

- **ImageExtension**: Generic image management with support for multiple image types, ordering, and featured images
- **SubdomainRedirect**: Flexible subdomain redirect system with support for different redirect types

## Installation

```bash
pip install django-essential-extensions
```

## Quick Start

1. Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'essential_extensions',
]
```

2. Run migrations:

```bash
python manage.py migrate
```

3. Add to your admin:

```python
# admin.py
from essential_extensions.admin import ImageExtensionAdmin, SubdomainRedirectAdmin
from essential_extensions.models import ImageExtension, SubdomainRedirect

admin.site.register(ImageExtension, ImageExtensionAdmin)
admin.site.register(SubdomainRedirect, SubdomainRedirectAdmin)
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
    order=1,
    is_featured=True
)
```

### Image Types

- `screenshot`: Game screenshots
- `banner`: Banner images
- `icon`: Icon images
- `custom`: Custom image types

## SubdomainRedirect

Manage subdomain redirects with different redirect types:

```python
from essential_extensions.models import SubdomainRedirect

# Redirect subdomain to a specific page
redirect = SubdomainRedirect.objects.create(
    subdomain='blog',
    redirect_type='page',
    redirect_path='/blog/',
    is_active=True
)
```

### Redirect Types

- `page`: Redirect to a specific page
- `object`: Redirect to a specific Django object
- `external`: Redirect to an external URL

## Configuration

You can configure which extensions are enabled in your Django settings:

```python
# settings.py
ESSENTIAL_EXTENSIONS_CONFIG = {
    'IMAGE_EXTENSION_ENABLED': True,
    'SUBDOMAIN_REDIRECT_ENABLED': True,
}
```

## Templates

### Image Extension

```html
{% load essential_extensions_tags %}

{% get_images_for_object game as images %}
{% for image in images %}
    <img src="{{ image.image.url }}" alt="{{ image.title }}">
{% endfor %}
```

### Subdomain Redirect

The subdomain redirects are handled automatically by the middleware.

## Development

```bash
# Clone the repository
git clone https://github.com/ghostjam/django-essential-extensions.git
cd django-essential-extensions

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support, please open an issue on GitHub or contact info@ghostjam.com. 