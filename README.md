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

4. The admin interface is automatically registered and ready to use.

## Basic Usage

### ImageExtension

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

### SubdomainRedirect

```python
from essential_extensions.models import SubdomainRedirect

# Redirect subdomain to a specific page
redirect = SubdomainRedirect.objects.create(
    subdomain='blog',
    redirect_type='full',
    redirect_path='/blog/',
    is_active=True
)
```

### SEOMixin

```python
from essential_extensions.mixins import SEOMixin

class GameProject(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    _seo = {
        'title': 'title',
        'description': 'description',
        'author': 'GhostJam Team',
    }
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

# SEO defaults
SEO_DEFAULTS = {
    'description': 'GhostJam - Indie Game Development Community',
    'keywords': ['indie games', 'game development'],
    'author': 'GhostJam Team',
    'robots': 'index, follow',
}
```

## Documentation

For detailed documentation on each component, see:

- **[ImageExtension](docs/image-extension.md)** - Complete guide to image management
- **[SubdomainRedirect](docs/subdomain-redirect-extension.md)** - Subdomain redirect system
- **[SEOMixin](docs/seo-extension.md)** - SEO optimization and meta tag management
- **[Middleware](docs/middleware.md)** - Admin IP restrictions and subdomain handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [GitHub Wiki](https://github.com/TUSKION/django-extensions/wiki)
- **Issues**: [GitHub Issues](https://github.com/TUSKION/django-extensions/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TUSKION/django-extensions/discussions)