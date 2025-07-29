from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('seo/meta_tags.html', takes_context=True)
def render_meta(context, obj=None, **overrides):
    """
    Render SEO meta tags from an object with SEO methods.
    
    Usage:
    {% render_meta meta %}  # Uses 'meta' from context
    {% render_meta object %}  # Uses specific object
    {% render_meta meta title="Custom Title" %}  # With overrides
    """
    # Get the meta object from context or parameter
    meta_obj = obj or context.get('meta') or context.get('object')
    
    if not meta_obj:
        return {}
    
    # Helper function to get SEO values with overrides
    def get_seo_value(field):
        # Check for override first
        if field in overrides:
            return overrides[field]
        
        # Try to call the SEO method (for model objects and meta classes)
        method_name = f'get_seo_{field}'
        if hasattr(meta_obj, method_name):
            method = getattr(meta_obj, method_name)
            if callable(method):
                return method()
        
        # Try direct dictionary key (for manual meta objects)
        if hasattr(meta_obj, '__getitem__'):
            try:
                return meta_obj[field]
            except (KeyError, TypeError):
                pass
        
        # Fallback to direct attribute
        return getattr(meta_obj, field, None)
    
    # Build meta data
    meta_data = {}
    
    # Standard meta fields
    for field in ['title', 'description', 'keywords', 'image', 'author', 'robots', 'canonical_url']:
        value = get_seo_value(field)
        if value:
            meta_data[field] = value
    
    return meta_data 