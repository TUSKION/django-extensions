# SEO Extension

The SEO Extension provides a flexible, mixin-based system for managing SEO metadata across Django models. It supports multiple data sources, fallback mechanisms, and template tags for easy integration.

## Features

- **Mixin-Based**: Easy to add SEO functionality to any model
- **Multiple Data Sources**: JSON field overrides, model field mapping, and defaults
- **Flexible Field Mapping**: Map SEO properties to model fields or static values
- **Template Tags**: Easy rendering of meta tags in templates
- **Fallback System**: Graceful degradation from overrides to defaults
- **Dynamic Keywords**: Automatic keyword generation from model fields
- **Settings Integration**: Configurable defaults via Django settings

## Models

### SEOMixin

The main mixin that provides SEO functionality to any model.

```python
class SEOMixin:
    # Map SEO property to a list of model fields to check in order
    SEO_FALLBACKS = {
        "title": ["title", "name"],
        "description": ["summary", "description"],
        "keywords": ["keywords"],
        "image": ["image"],
        "author": ["author"],
        "robots": ["robots"],
        "canonical_url": ["canonical_url"],
    }

    def get_seo_value(self, key, default=None):
        """Get SEO value with priority: extra_data > _seo mapping > default"""
        # Implementation details...

    def get_seo_title(self):
        """Get SEO title"""
        return self.get_seo_value("title", "")

    def get_seo_description(self):
        """Get SEO description"""
        return self.get_seo_value("description", getattr(settings, 'SEO_DEFAULTS', {}).get('description', ''))

    def get_seo_keywords(self):
        """Get SEO keywords as list"""
        # Implementation with dynamic keyword generation...

    def get_seo_image(self):
        """Get SEO image URL"""
        return self.get_seo_value("image", getattr(settings, 'SEO_DEFAULTS', {}).get('image', ''))

    def get_seo_author(self):
        """Get SEO author"""
        return self.get_seo_value("author", getattr(settings, 'SEO_DEFAULTS', {}).get('author', ''))

    def get_seo_robots(self):
        """Get SEO robots directive"""
        return self.get_seo_value("robots", getattr(settings, 'SEO_DEFAULTS', {}).get('robots', 'index, follow'))

    def get_seo_canonical_url(self):
        """Get SEO canonical URL"""
        return self.get_seo_value("canonical_url", "")
```

## Template Tags

### Loading the Tags

```django
{% load seo_tags %}
```

### Rendering Meta Tags

```django
{% render_meta object %}
{% render_meta object title="Custom Title" description="Custom Description" %}
{% render_meta meta %}
```

### Meta Tag Template

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

## Python Usage

### Adding SEO to a Model

```python
from extensions.mixins import SEOMixin

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
        'author': 'GameJam Studios',  # Static value
        'keyword_categories': 'categories',  # Dynamic keywords from categories
    }
    
    def get_absolute_url(self):
        return reverse('game_detail', args=[self.slug])
```

### Using SEO Methods

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

# Get any SEO value
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

## Settings Configuration

### SEO Defaults

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

### Custom Settings

```python
# settings.py

# Custom SEO settings
SEO_DEFAULT_TITLE_SUFFIX = ' - GhostJam'
SEO_MAX_DESCRIPTION_LENGTH = 160
SEO_MAX_KEYWORDS = 10
```

## Examples

### Game Detail Page

```python
# views.py
def game_detail(request, slug):
    game = get_object_or_404(GameProject, slug=slug)
    
    # Create meta object for template
    meta = {
        'title': game.get_seo_title(),
        'description': game.get_seo_description(),
        'keywords': game.get_seo_keywords(),
        'image': game.get_seo_image(),
        'author': game.get_seo_author(),
        'canonical_url': request.build_absolute_uri(game.get_absolute_url()),
    }
    
    return render(request, 'games/detail.html', {
        'game': game,
        'meta': meta
    })
```

```django
<!-- games/detail.html -->
{% extends "base.html" %}
{% load seo_tags %}

{% block head %}
    {% render_meta meta %}
{% endblock %}

{% block content %}
    <h1>{{ game.title }}</h1>
    <p>{{ game.description }}</p>
    <!-- Rest of game content -->
{% endblock %}
```

### Blog Post with Overrides

```python
# views.py
def blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    return render(request, 'blog/post.html', {
        'post': post,
        'meta': post  # Pass the post object directly
    })
```

```django
<!-- blog/post.html -->
{% extends "base.html" %}
{% load seo_tags %}

{% block head %}
    {% render_meta post %}
{% endblock %}

{% block content %}
    <article>
        <h1>{{ post.title }}</h1>
        {{ post.content|safe }}
    </article>
{% endblock %}
```

### Custom Meta with Overrides

```django
{% load seo_tags %}

{% render_meta post title="Custom Blog Title" description="Custom description for this post" %}
```

### SEO with Extra Data Overrides

```python
# Using extra_data JSON field for SEO overrides
game = GameProject.objects.get(title='Amazing Game')

# Set SEO overrides in extra_data
game.extra_data = {
    'title': 'Custom SEO Title for Amazing Game',
    'description': 'Custom SEO description that overrides the default',
    'keywords': ['custom', 'keywords', 'for', 'this', 'game'],
    'image': '/static/images/custom-og-image.jpg',
}
game.save()

# These will now use the extra_data values
title = game.get_seo_title()  # Returns "Custom SEO Title for Amazing Game"
description = game.get_seo_description()  # Returns custom description
```

## Data Source Priority

The SEO system uses a priority-based approach for getting values:

1. **extra_data JSON field** (highest priority)
2. **_seo field mapping** (model fields or static values)
3. **Settings defaults** (lowest priority)

### Example Priority Chain

```python
class GameProject(models.Model, SEOMixin):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    extra_data = models.JSONField(default=dict, blank=True)
    
    _seo = {
        'title': 'title',
        'description': 'summary',
        'author': 'GhostJam Team',
    }

# Priority for description:
# 1. extra_data.get('description') - if exists
# 2. self.summary - if exists and not empty
# 3. settings.SEO_DEFAULTS.get('description') - if exists
# 4. '' (empty string) - final fallback
```

## Dynamic Keyword Generation

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

## Best Practices

### Model Configuration

1. **Use descriptive field mapping**: Map SEO fields to appropriate model fields
2. **Provide fallbacks**: Always have sensible defaults
3. **Use static values**: For consistent values like author or robots
4. **Leverage dynamic keywords**: Automatically generate keywords from related fields

### Template Usage

1. **Use the meta object**: Pass a meta object to templates for consistency
2. **Provide overrides**: Allow custom meta tags when needed
3. **Check for existence**: Always verify meta data exists before using
4. **Use canonical URLs**: Always provide canonical URLs for SEO

### Data Management

1. **Keep extra_data clean**: Use extra_data for overrides, not primary data
2. **Update regularly**: Keep SEO data current with content changes
3. **Test meta tags**: Verify meta tags render correctly
4. **Monitor performance**: Ensure SEO methods don't impact performance

## Troubleshooting

### Common Issues

1. **Meta tags not showing**: Check if the object has SEO methods
2. **Wrong values**: Verify the data source priority chain
3. **Performance issues**: Ensure SEO methods are efficient
4. **Missing defaults**: Check if settings.SEO_DEFAULTS is configured

### Debug Tips

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

### Template Debugging

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

## API Reference

### SEOMixin Methods

- `get_seo_value(key, default=None)`: Get any SEO value with fallbacks
- `get_seo_title()`: Get SEO title
- `get_seo_description()`: Get SEO description
- `get_seo_keywords()`: Get SEO keywords as list
- `get_seo_image()`: Get SEO image URL
- `get_seo_author()`: Get SEO author
- `get_seo_robots()`: Get SEO robots directive
- `get_seo_canonical_url()`: Get SEO canonical URL

### Template Tags

- `render_meta(context, obj=None, **overrides)`: Render SEO meta tags

### Configuration

- `_seo`: Class attribute mapping SEO properties to model fields
- `SEO_DEFAULTS`: Settings dictionary for default SEO values
- `extra_data`: JSON field for SEO overrides 