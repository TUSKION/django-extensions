# Subdomain Redirect Extension

The Subdomain Redirect Extension provides a flexible system for managing subdomain redirects to the main domain. It supports both full redirects and path-preserving redirects, with optional attachment to any Django model.

## Features

- **Generic Attachment**: Optionally attach redirects to any Django model
- **Multiple Redirect Types**: Full redirects and path-preserving redirects
- **Middleware Integration**: Automatic redirect handling via middleware
- **Active/Inactive Status**: Control redirect visibility
- **Admin Interface**: Full admin interface with validation
- **Subdomain Validation**: Automatic subdomain format validation
- **Flexible Configuration**: Support for both standalone and model-attached redirects

## Models

### SubdomainRedirect

The main model for storing subdomain redirect data.

```python
class SubdomainRedirect(models.Model):
    # Optional generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Subdomain configuration
    subdomain = models.CharField(max_length=100, unique=True)
    
    # Redirect configuration
    redirect_type = models.CharField(max_length=20, choices=REDIRECT_TYPE_CHOICES)
    redirect_path = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Redirect Types

- **Full Redirect**: Redirect to a specific path on the main domain
- **Path Preserving**: Keep the same path when redirecting to the main domain

## Middleware

### SubdomainRedirectMiddleware

The middleware automatically handles subdomain redirects:

```python
class SubdomainRedirectMiddleware:
    def __call__(self, request):
        # Get the hostname from the request
        hostname = request.get_host().split(':')[0].lower()
        
        # Get the main domain from settings
        main_domain = getattr(settings, 'MAIN_DOMAIN', 'example.com')
        
        # Only redirect if this is a subdomain of the main domain
        if hostname.endswith('.' + main_domain):
            subdomain = hostname.rsplit('.' + main_domain, 1)[0]
            
            # Skip if it's the main domain itself or www
            if subdomain and subdomain not in ['', 'www']:
                # Look for a redirect for this subdomain
                redirect_obj = SubdomainRedirect.get_redirect_for_subdomain(subdomain)
                
                if redirect_obj:
                    # Determine the redirect path
                    if redirect_obj.redirect_type == SubdomainRedirect.REDIRECT_TYPE_FULL:
                        # For full redirects, use object's absolute URL if available, otherwise use redirect_path
                        if redirect_obj.content_object and hasattr(redirect_obj.content_object, 'get_absolute_url'):
                            redirect_path = redirect_obj.content_object.get_absolute_url()
                        else:
                            redirect_path = redirect_obj.redirect_path
                    else:
                        # For path-preserving redirects, keep the same path
                        redirect_path = request.path
                    
                    # Build the full redirect URL to the main domain
                    protocol = 'https' if request.is_secure() else 'http'
                    redirect_url = f"{protocol}://{main_domain}{redirect_path}"
                    
                    # Perform the redirect
                    return redirect(redirect_url, permanent=True)
        
        # No redirect found, continue with normal response
        return self.get_response(request)
```

## Python Usage

### Basic Usage

```python
from extensions.models.SubdomainRedirect import SubdomainRedirect

# Create a full redirect
redirect = SubdomainRedirect.objects.create(
    subdomain='gamex',
    redirect_type=SubdomainRedirect.REDIRECT_TYPE_FULL,
    redirect_path='/game/game-x/',
    is_active=True
)

# Create a path-preserving redirect
redirect = SubdomainRedirect.objects.create(
    subdomain='blog',
    redirect_type=SubdomainRedirect.REDIRECT_TYPE_PATH_PRESERVE,
    is_active=True
)
```

### Getting Redirects

```python
# Get redirect for a specific subdomain
redirect = SubdomainRedirect.get_redirect_for_subdomain('gamex')

# Get all active redirects
active_redirects = SubdomainRedirect.objects.filter(is_active=True)

# Get redirects attached to a specific object
game_redirects = SubdomainRedirect.objects.filter(
    content_type=ContentType.objects.get_for_model(game),
    object_id=game.id
)
```

### Redirect URL Generation

```python
# Get the redirect URL for a request path
redirect_url = redirect.get_redirect_url('/lol/')

# For full redirects, this returns the redirect_path
# For path-preserving redirects, this returns the request path
```

## Admin Interface

### SubdomainRedirectAdmin

The admin interface provides:

- **Generic Object Selector**: Optional dropdown to select the object to attach redirects to
- **Subdomain Validation**: Automatic subdomain format validation
- **Redirect Type Configuration**: Easy selection of redirect type
- **Organized Fieldsets**: Logical grouping of fields
- **Validation**: Ensures proper redirect configuration

### Inline Usage

```python
from extensions.admin import SubdomainRedirectAdmin

# Register in admin.py
admin.site.register(SubdomainRedirect, SubdomainRedirectAdmin)
```

## Settings Configuration

### Required Settings

```python
# settings.py

# Main domain for redirects
MAIN_DOMAIN = 'example.com'

# Add middleware to MIDDLEWARE setting
MIDDLEWARE = [
    # ... other middleware
    'extensions.middleware.SubdomainRedirectMiddleware',
    # ... other middleware
]
```

### Optional Settings

```python
# settings.py

# Custom main domain (if different from ALLOWED_HOSTS)
MAIN_DOMAIN = 'ghostjam.com'

# Additional subdomains to ignore (beyond 'www')
IGNORED_SUBDOMAINS = ['api', 'admin', 'static']
```

## Examples

### Game-Specific Subdomain Redirect

```python
# Create a redirect for a specific game
game = GameProject.objects.get(title='Amazing Game')

redirect = SubdomainRedirect.objects.create(
    subdomain='amazing-game',
    redirect_type=SubdomainRedirect.REDIRECT_TYPE_FULL,
    content_type=ContentType.objects.get_for_model(game),
    object_id=game.id,
    is_active=True
)

# The redirect will use game.get_absolute_url() if available
# Otherwise, it will use the redirect_path field
```

### Blog Subdomain Redirect

```python
# Create a path-preserving redirect for blog
redirect = SubdomainRedirect.objects.create(
    subdomain='blog',
    redirect_type=SubdomainRedirect.REDIRECT_TYPE_PATH_PRESERVE,
    is_active=True
)

# This will redirect:
# blog.example.com/2023/01/post-title/ -> example.com/2023/01/post-title/
```

### API Subdomain Redirect

```python
# Create a full redirect for API
redirect = SubdomainRedirect.objects.create(
    subdomain='api',
    redirect_type=SubdomainRedirect.REDIRECT_TYPE_FULL,
    redirect_path='/api/v1/',
    is_active=True
)

# This will redirect:
# api.example.com/anything -> example.com/api/v1/
```

## URL Patterns

### Full Redirect Examples

| Subdomain | Redirect Path | Result |
|-----------|---------------|---------|
| gamex | /game/game-x/ | gamex.example.com → example.com/game/game-x/ |
| api | /api/v1/ | api.example.com/anything → example.com/api/v1/ |
| docs | /documentation/ | docs.example.com → example.com/documentation/ |

### Path Preserving Examples

| Subdomain | Request Path | Result |
|-----------|--------------|---------|
| blog | /2023/01/post-title/ | blog.example.com/2023/01/post-title/ → example.com/2023/01/post-title/ |
| forum | /category/general/ | forum.example.com/category/general/ → example.com/category/general/ |
| wiki | /page/installation/ | wiki.example.com/page/installation/ → example.com/page/installation/ |

## Validation

### Subdomain Format Validation

The system automatically validates subdomain format:

```python
# Valid subdomains
'gamex'      # ✅ Valid
'my-game'    # ✅ Valid
'api_v2'     # ✅ Valid
'123'        # ✅ Valid

# Invalid subdomains
'game.x'     # ❌ Contains dots
'game x'     # ❌ Contains spaces
'a'          # ❌ Too short (minimum 2 characters)
'game@x'     # ❌ Contains invalid characters
```

### Redirect Configuration Validation

- **Full Redirects**: Must have a redirect_path
- **Path Preserving Redirects**: Should not have a redirect_path
- **Unique Subdomains**: Each subdomain can only have one redirect

## Best Practices

### Subdomain Naming

1. **Use descriptive names**: Choose clear, memorable subdomain names
2. **Keep it short**: Use concise names when possible
3. **Use hyphens**: Separate words with hyphens (e.g., 'my-game')
4. **Avoid conflicts**: Don't use reserved subdomains like 'www', 'api', 'admin'

### Redirect Configuration

1. **Choose appropriate type**: Use full redirects for specific pages, path-preserving for sections
2. **Test redirects**: Verify redirects work correctly in all environments
3. **Monitor performance**: Ensure redirects don't impact site performance
4. **Keep active**: Use the is_active field to disable redirects when needed

### Security Considerations

1. **Validate subdomains**: Ensure subdomain format is valid
2. **Limit redirects**: Don't create too many redirects
3. **Monitor usage**: Watch for abuse of redirect functionality
4. **Secure middleware**: Ensure middleware is properly configured

## Troubleshooting

### Common Issues

1. **Redirects not working**: Check if middleware is properly configured
2. **Infinite redirects**: Ensure redirect paths don't create loops
3. **Subdomain validation errors**: Check subdomain format
4. **Middleware conflicts**: Ensure middleware order is correct

### Debug Tips

```python
# Check if redirect exists for a subdomain
from extensions.models.SubdomainRedirect import SubdomainRedirect

redirect = SubdomainRedirect.get_redirect_for_subdomain('gamex')
if redirect:
    print(f"Found redirect: {redirect}")
    print(f"Type: {redirect.redirect_type}")
    print(f"Path: {redirect.redirect_path}")
    print(f"Active: {redirect.is_active}")
else:
    print("No redirect found for 'gamex'")

# Check all active redirects
active_redirects = SubdomainRedirect.objects.filter(is_active=True)
for redirect in active_redirects:
    print(f"{redirect.subdomain} -> {redirect.get_redirect_url('/test/')}")
```

### Middleware Debugging

```python
# Add debug logging to middleware
import logging
logger = logging.getLogger(__name__)

class SubdomainRedirectMiddleware:
    def __call__(self, request):
        hostname = request.get_host().split(':')[0].lower()
        logger.debug(f"Processing request for hostname: {hostname}")
        
        # ... rest of middleware logic
```

## API Reference

### Model Methods

- `get_redirect_url(request_path='/')`: Get the redirect URL for a request path
- `clean()`: Validate the subdomain format and redirect configuration
- `__str__()`: String representation of the redirect

### Class Methods

- `get_redirect_for_subdomain(subdomain)`: Get the active redirect for a given subdomain

### Model Properties

- `content_object`: The object this redirect is attached to (optional)
- `subdomain`: The subdomain to redirect from
- `redirect_type`: The type of redirect (full or path-preserving)
- `redirect_path`: The path to redirect to (for full redirects)
- `is_active`: Whether this redirect is active

### Constants

- `REDIRECT_TYPE_FULL`: Full redirect type
- `REDIRECT_TYPE_PATH_PRESERVE`: Path-preserving redirect type 